# Journey-101

> 여행이 두렵지만 가보고 싶은 사람들을 위한 단계형 관광 지원 서비스.

## 핵심 목표

- 수준별 제안 - 초보 여행자가 자신의 현재 상태에 맞는 낮은 난이도의 관광 경험부터 시작할 수 있게 제안
- 점진적 확대 - 피드백을 통해 점진적으로 관광 범위를 넓힐 수 있도록 보조

## 문서

- [온보딩](docs/team-rules/README.md)
  - [환경설정](docs/setup.md)

- [제품 기획서](docs/spec.md)
- [기능 개발 계획](docs/plan.md)

## 개발 베이스라인

이 레포지토리는 React frontend, FastAPI backend, PostgreSQL database를
Docker Compose로 함께 실행하는 모노레포 구조를 사용합니다.

```txt
frontend/   React, Vite, TypeScript
backend/    FastAPI, SQLAlchemy, PostgreSQL client, uv
postgres    Docker Compose PostgreSQL service
```

## 실행 방법

```sh
cp .env.example .env
docker compose up --build
```

실행 후 브라우저에서 아래 주소로 접속합니다.

```txt
http://localhost:5173
```

로컬 PostgreSQL과 포트가 충돌하면 `.env`의 `POSTGRES_HOST_PORT` 값을
변경합니다.

## 환경변수

`.env`는 커밋하지 않습니다. 새 환경에서는 `.env.example`을 복사해 사용합니다.

주요 값:

- `DATABASE_URL`: backend가 우선 사용하는 DB 연결 문자열
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: PostgreSQL 초기값
- `POSTGRES_HOST`, `POSTGRES_PORT`: backend 컨테이너 내부 DB 접속 정보
- `POSTGRES_HOST_PORT`: 로컬 머신에 노출할 PostgreSQL 포트

## API

- `GET /api/v1/health`
- `GET /api/v1/health/db`

응답은 기능 API에서 공통으로 사용할 수 있도록 아래 형태를 따릅니다.

```json
{
  "success": true,
  "data": {}
}
```

## 검증 방법

1. `http://localhost:5173`에 접속합니다.
2. `Backend Health Check` 버튼을 클릭해 backend 응답을 확인합니다.
3. `DB Health Check` 버튼을 클릭해 PostgreSQL `SELECT 1` 결과를 확인합니다.

Backend 테스트는 uv 기반으로 실행합니다.

```sh
cd backend
uv run pytest
```

## 확장 규칙

- Backend는 domain 단위로 `router.py`, `service.py`, `schemas.py`를 둡니다.
- Backend API는 `/api/v1` prefix 아래에 추가합니다.
- Backend 환경변수 접근은 `backend/app/core/config.py`로 제한합니다.
- Backend DB 연결은 `backend/app/db/session.py`에서 관리합니다.
- Frontend 의존 방향은 `pages -> features -> shared`를 유지합니다.
- Frontend API 호출은 `frontend/src/shared/api/client.ts`를 경유합니다.
- 외부 API client는 `backend/app/integrations` 아래에 추가합니다.
