# Trips API

변경일: 2026-08-12

모든 엔드포인트에 `Authorization: Bearer <firebase-id-token>`이 필요하다. 검증된
UID가 유일한 소유자 식별자이며 request와 response에 `user_id`는 없다.

- `GET /api/v1/trips`
- `POST /api/v1/trips` with `{"title":"북촌 산책"}`
- `GET /api/v1/trips/{trip_id}`
- `PATCH /api/v1/trips/{trip_id}` with `{"title":"새 제목"}`
- `POST /api/v1/trips/{trip_id}/attempts`
- `PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}`
- `PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}/feedback`

## FE가 지켜야 할 계약

- 목록 조회는 `GET /api/v1/trips`이며 `?user_id=...`를 붙이지 않는다.
- 생성 body는 `{"title":"북촌 산책"}`뿐이다.
- Trip 목록과 상세 응답에는 `id`, `title`, attempt 정보만 있고 `user_id`가 없다.
- Trip 생성 성공 status는 `201`이며 기본 `started` attempt가 함께 생성된다.
- Attempt 생성 성공 status도 `201`이다.
- 다른 사용자의 trip을 조회하거나 수정하면 attempt 작업을 포함해 `404`다.
- request body의 추가 필드는 `422`다.
