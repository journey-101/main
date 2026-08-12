# Preferences and Recommendations API 계약

변경일: 2026-08-12

모든 엔드포인트에 `Authorization: Bearer <firebase-id-token>`이 필요하다. 사용자는
토큰에서 결정되며 request와 response 어디에도 `user_id`가 없다.

- `GET /api/v1/me/preferences`
- `PUT /api/v1/me/preferences`
- `POST /api/v1/recommendations`
- `POST /api/v1/recommendations/places`
- `POST /api/v1/recommendations/trips`

## 선호도

`GET /api/v1/me/preferences`에는 query parameter가 없다. 저장된 선호도가 없으면
`404 {"detail":"User preference not found"}`를 반환한다.

`PUT /api/v1/me/preferences` body:

```json
{
  "preferred_categories": ["museum", "park"],
  "avoided_categories": ["concert_hall"],
  "prefers_quiet": true,
  "max_walk_minutes": 20,
  "is_first_time_traveler": true
}
```

응답 `data`도 같은 다섯 필드이며 `user_id`는 없다. `max_walk_minutes`는 1 이상이고
추가 필드는 `422`다.

## 추천

- `/recommendations/places`: body는 `region_code`(선택), `limit`(기본 10)
- `/recommendations/trips`: body는 `trip_id`, `limit`(기본 10)
- `/recommendations`: body는 `method`, `target`, `limit`

`limit`은 1~100이다. Trip 대상 추천은 토큰 사용자가 소유한 trip에만 접근하며,
존재하지 않거나 다른 사용자의 trip이면 모두 `404 {"detail":"Trip not found"}`를
반환한다. FE는 이 두 경우를 구분할 수 없고 구분해서도 안 된다.
