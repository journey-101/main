# FE API 연동 가이드

변경일: 2026-08-12
기준 브랜치: `feat/33-cloud-sql-firebase-auth`

이 문서는 FE가 이 브랜치를 연동할 때 필요한 외부 API 변경만 정리한다. Cloud SQL,
PostGIS, repository/UoW, Alembic은 BE 내부 구현이므로 FE 계약이 아니다.

## 결론

`dev`의 directions 기능을 이 브랜치에 병합하면서 directions의 endpoint, request,
response는 변경하지 않았다. 내부 장소 조회만 기존 SQLAlchemy 직접 호출에서 현재
브랜치의 PostGIS repository로 교체했다.

반면 이 브랜치 전체에는 Firebase Auth 전환에 따른 FE 계약 변경이 있다. trips,
preferences, recommendations는 테스트 UUID 대신 Firebase ID 토큰으로 현재 사용자를
식별한다.

## 인증 범위

| API | 인증 | 사용자 식별 |
| --- | --- | --- |
| `/api/v1/health/**` | 불필요 | 해당 없음 |
| `/api/v1/places/**` | 불필요 | 해당 없음 |
| `/api/v1/directions/**` | 불필요 | 해당 없음 |
| `/api/v1/auth/me` | Bearer 토큰 | Firebase ID 토큰 |
| `/api/v1/trips/**` | Bearer 토큰 | Firebase ID 토큰 |
| `/api/v1/me/preferences` | Bearer 토큰 | Firebase ID 토큰 |
| `/api/v1/recommendations/**` | Bearer 토큰 | Firebase ID 토큰 |

인증 요청 형식:

```http
Authorization: Bearer <firebase-id-token>
```

토큰이 없거나 유효하지 않으면 `401`이다. 보호된 리소스가 없거나 다른 사용자
소유이면 정보 노출을 막기 위해 동일하게 `404`를 반환한다.

## dev 대비 FE 변경 사항

| 기존 호출 | 현재 호출 |
| --- | --- |
| `GET /trips?user_id={uuid}` | `GET /trips` + Bearer 토큰 |
| `POST /trips` body의 `user_id` | `user_id` 제거 + Bearer 토큰 |
| `GET /me/preferences?user_id={uuid}` | query 제거 + Bearer 토큰 |
| `PUT /me/preferences` body의 `user_id` | `user_id` 제거 + Bearer 토큰 |
| 추천 body의 `user_id` | `user_id` 제거 + Bearer 토큰 |
| 응답의 `user_id` 사용 | 응답에서 제거 |

현재 FE 코드에는 아직 `VITE_TEST_USER_ID`, `getTestUserId()`, `user_id` query/body가
남아 있다. 이 브랜치를 연동할 때는 해당 경로를 제거하고 공통 API client가 Firebase
ID 토큰을 헤더에 넣도록 변경해야 한다. `user_id`를 계속 보내면 strict schema에서
`422`가 발생한다.

## 변경되지 않은 계약

- API prefix는 `/api/v1`이다.
- 성공 응답 wrapper는 `{ "success": true, "data": ... }`다.
- places의 `lat`, `lng` 필드와 directions의 좌표 순서는 유지된다.
- directions `geometry.coordinates`는 GeoJSON 순서인 `[longitude, latitude]`다.
- directions는 공개 API이며 `POST /api/v1/directions/search`를 유지한다.

## FE 구현 체크리스트

1. Firebase 로그인 완료 전에는 인증 API를 호출하지 않는다.
2. 공통 API client에서 요청 시점의 ID 토큰을 얻어 `Authorization` 헤더에 넣는다.
3. trips, preferences, recommendations의 `user_id` 타입과 전송 코드를 제거한다.
4. `401`은 재로그인 또는 인증 갱신 흐름으로, `404`는 리소스 없음으로 처리한다.
5. directions 지도 좌표는 `[lng, lat]` 순서로 사용한다.

세부 payload와 response model은 각 도메인 계약 문서를 따른다.
