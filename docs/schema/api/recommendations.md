# Preferences and recommendations API

All endpoints require `Authorization: Bearer <firebase-id-token>` and derive the
user from that token. No request or response contains `user_id`.

- `GET /api/v1/me/preferences`
- `PUT /api/v1/me/preferences`
- `POST /api/v1/recommendations`
- `POST /api/v1/recommendations/places`
- `POST /api/v1/recommendations/trips`

Preference bodies contain `preferred_categories`, `avoided_categories`,
`prefers_quiet`, `max_walk_minutes`, and `is_first_time_traveler`. Trip-targeted
recommendations enforce ownership and return `404` for another user's trip.
