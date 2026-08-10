# Trips API

Every endpoint requires `Authorization: Bearer <firebase-id-token>`. The verified
UID is the sole owner identifier and is absent from requests and responses.

- `GET /api/v1/trips`
- `POST /api/v1/trips` with `{"title":"북촌 산책"}`
- `GET /api/v1/trips/{trip_id}`
- `PATCH /api/v1/trips/{trip_id}` with `{"title":"새 제목"}`
- `POST /api/v1/trips/{trip_id}/attempts`
- `PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}`
- `PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}/feedback`

Trip list/detail objects contain `id`, `title`, and attempt data, but no `user_id`.
Reading or mutating a trip owned by another UID returns `404`, including attempt
operations. Creating a trip and its initial `started` attempt is one transaction.
