# Cloud SQL·Firebase Auth 전환 직전 정리 계획

## 요약

- 애플리케이션 데이터는 PostgreSQL/PostGIS에 유지하고 Firestore와 Data Connect는 사용하지 않는다.
- Firebase는 Auth에만 사용한다. 백엔드는 Firebase ID 토큰을 검증하며, 프런트는 후속 작업에서 Bearer 토큰만 전달하면 된다. 이 방식은 [Firebase 공식 백엔드 인증 흐름](https://firebase.google.com/docs/auth/admin/verify-id-tokens)을 따른다.
- 이번 작업은 로컬 PostgreSQL/PostGIS와 Auth Emulator에서 모든 기능·마이그레이션을 검증하는 단계까지다. 실제 Cloud SQL 생성, 운영 자격증명 주입, 운영 전환은 포함하지 않는다.
- Cloud SQL은 PostGIS를 공식 지원하므로 동일한 마이그레이션을 그대로 적용한다. [Cloud SQL PostGIS 지원 문서](https://docs.cloud.google.com/sql/docs/postgres/extensions)

## 구현 변경

### 인증과 API 계약

- Firebase Admin SDK 기반 `TokenVerifier`와 FastAPI `CurrentUser` 의존성을 추가한다.
- 로컬은 Firebase Auth Emulator, 클라우드는 ADC와 `GOOGLE_CLOUD_PROJECT`만 바꿔 동작하도록 구성한다.
- `GET /api/v1/auth/me`를 추가해 검증된 `uid`, 이메일, 표시 이름, provider 정보를 반환한다.
- 여행·선호도·추천 API는 모두 Bearer 인증을 필수화한다. 장소·health API는 공개 상태를 유지한다.
- 인증된 사용자는 SQL의 로컬 사용자 참조 행에 idempotent하게 등록한다. Firebase가 계정 원장이고 SQL 행은 외래 키 무결성을 위한 projection으로만 취급한다.
- 기존 UUID 사용자 호환은 제공하지 않는다.
  - 요청의 `user_id` query/body 필드를 전부 제거한다.
  - 여행·선호도 응답에서도 `user_id`를 제거한다.
  - UID는 검증된 토큰에서만 가져오며 클라이언트가 다른 사용자를 지정할 수 없게 한다.
  - 여행 상세·수정·시도 API의 SQL 조건에도 UID 소유권을 포함해 타 사용자 접근을 404로 처리한다.
- 프런트 코드는 이번 범위에서 수정하지 않고, 변경된 OpenAPI 계약과 `Authorization: Bearer` 연결 예시만 문서화한다.

### SQL 경계와 트랜잭션

- 서비스와 라우터에서 `SQLAlchemy Session`, `RowMapping`, SQL 예외 의존성을 제거한다.
- 도메인별 repository protocol과 타입이 지정된 record를 정의하고 PostgreSQL 구현체 내부에만 명시적 SQL을 둔다.
- 요청 단위 Unit of Work가 연결·commit·rollback을 관리한다.
- 여행과 첫 시도 생성, 선호도 upsert, 관심 지역 일괄 교체는 각각 하나의 트랜잭션으로 처리한다.
- 추천 서비스는 `TripRepository`, `PreferenceRepository`, `PlaceRepository`를 조합하며 다른 도메인의 SQL 구현을 직접 import하지 않는다.
- 장소 검색의 키워드·지역·카테고리·반경·limit 필터를 Python 전체 로딩 대신 SQL/PostGIS 질의로 이동한다.
- SQLite로 복제된 테스트 DDL은 제거하고 PostgreSQL/PostGIS 통합 테스트와 서비스 단위 테스트를 분리한다.

### 스키마와 GIS 정리

- Docker 초기화 SQL을 스키마 원본으로 사용하지 않고 Alembic을 유일한 마이그레이션 수단으로 전환한다.
- 로컬 DB 이미지를 PostgreSQL 16 + PostGIS 3.5 계열로 교체하고 `pgcrypto`, `postgis` 확장을 마이그레이션에서 활성화한다.
- 주요 스키마는 다음으로 정리한다.
  - `app_users(firebase_uid PK, created_at, updated_at)`: Firebase 계정 참조만 저장
  - `user_preferences(firebase_uid PK/FK, preferred_categories text[], avoided_categories text[], …)`: JSON 문자열 컬럼 제거
  - `trips(id UUID PK, firebase_uid FK, title, created_at, updated_at)`
  - `trip_attempts(id UUID PK, trip_id FK, status CHECK, feedback_text, created_at, updated_at)`
  - `regions(id UUID PK, code UNIQUE, name, boundary geometry(MultiPolygon,4326), timestamps)`
  - `places(..., region_id FK, location geography(Point,4326), ...)`: 중복 좌표 원본을 제거하고 API의 lat/lng는 `location`에서 계산
  - `user_interest_regions(firebase_uid, region_id, created_at, PK(firebase_uid, region_id))`
- `regions.boundary`, `places.location`에 GiST 인덱스를 추가하고 최신 시도 조회용 `(trip_id, created_at DESC, id DESC)` 인덱스를 둔다.
- 관심 지역 repository에는 사용자별 목록 조회와 원자적 전체 교체 기능을 구현한다. 공개 API는 후속 작업으로 남긴다.
- 실제 지역 경계 import는 GeoJSON 입력을 받도록 만들고, 누락된 지역 코드나 유효하지 않은 geometry가 있으면 전체 import를 실패시킨다.

### 기존 데이터 마이그레이션과 클라우드 준비

- 현재 스키마를 표현하는 Alembic legacy baseline과 정리 revision을 만든다. 기존 DB는 구조 검증 후 baseline stamp, 새 DB는 처음부터 전체 revision을 적용한다.
- `legacy_user_uuid,firebase_uid` CSV 매핑을 필수 입력으로 받는 일회성 migration command를 제공한다. 매핑되지 않은 사용자나 중복 UID가 있으면 변경 전에 중단한다.
- 정리 migration은 사용자 FK, 선호도 배열, 장소 좌표, 지역 참조를 변환한 뒤 건수·고아 FK·중복·geometry 유효성을 검증하고 구 컬럼을 제거한다.
- 운영용 단일 전환 runbook은 `쓰기 중지 → 백업 → Firebase 사용자/UID 매핑 확정 → Alembic 적용 → 데이터 import → 검증 → 신버전 배포 → 구 DB 읽기 전용` 순서로 준비한다.
- 설정은 로컬/Cloud SQL 모두 하나의 `DATABASE_URL` 계약을 사용하고 pool 크기·timeout을 환경변수화한다. Firebase는 ADC 또는 Emulator 환경변수만 사용하며 서비스 계정 JSON을 저장소에 두지 않는다.
- Compose seed는 별도 idempotent seed command로 이전해 운영 마이그레이션과 분리한다.

## 테스트 및 승인 기준

- Firebase Auth Emulator의 정상 토큰으로 `/auth/me`와 보호 API가 동작하고, 누락·변조·만료·취소된 토큰은 401을 반환한다.
- 토큰 UID가 요청 데이터보다 유일한 사용자 식별 근거이며 다른 사용자의 여행 조회·수정·시도가 불가능하다.
- 여행 생성 실패 시 첫 시도를 포함해 rollback되고, 최신 시도 선택 순서가 기존 동작과 같다.
- PostGIS 반경 검색, 지역 polygon 포함 여부, 경계 인접 사례, 잘못된 geometry, GiST 인덱스 사용을 검증한다.
- legacy fixture에 UUID→UID migration을 실행해 테이블별 건수, FK, 배열 값, 장소 좌표가 보존됨을 확인한다.
- 빈 DB 전체 migration, 기존 DB upgrade, seed 재실행, migration 실패 시 rollback을 각각 테스트한다.
- 전체 백엔드 API 테스트, lint, migration check와 로컬 Compose smoke test가 통과해야 한다.
- 최종 상태에서는 소스 코드에서 SQLAlchemy session이 router/service에 노출되지 않고, raw SQL은 PostgreSQL repository와 migration에만 존재해야 한다.

## 확정된 가정

- 최종 저장소는 Cloud SQL 직접 연결이며 Firebase Data Connect와 Firestore는 사용하지 않는다.
- 첫 인증 제공자는 Google이며, 실제 로그인 UI와 Firebase Client SDK 연결은 후속 프런트 작업이다.
- 사용자 UUID의 이전 호환 경로나 dual-read/dual-write는 만들지 않는다.
- 관심 지역은 사용자 정의 도형이 아니라 관리되는 지역 Polygon을 사용자가 참조하는 모델이다.
- 실제 클라우드 자원 생성과 데이터 cutover는 이번 로컬 정리가 끝난 다음 작업에서 수행한다.
