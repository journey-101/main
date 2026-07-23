# Recommendations API 계약

기본 경로는 `/api/v1`이며 성공 응답은 공통 wrapper인
`{ "success": true, "data": ... }`를 사용한다.

## Preferences API

```http
GET /api/v1/me/preferences?user_id={UUID}
PUT /api/v1/me/preferences
```

`GET`은 사용자의 저장된 여행 성향을 반환한다. 사용자 없으면
`404 {"detail":"User not found"}`, 성향이 없으면
`404 {"detail":"User preference not found"}`다.

`PUT` body는 `user_id`, `preferred_categories`, `avoided_categories`,
`prefers_quiet`, `max_walk_minutes`, `is_first_time_traveler`를 받는다.
category 필드는 `list[str]`이고 `max_walk_minutes`는 1 이상이다. extra field와
잘못된 UUID/body는 `422`다. 기존 성향은 갱신하고 없으면 생성한다.

## Recommendation API

```http
POST /api/v1/recommendations
POST /api/v1/recommendations/places
POST /api/v1/recommendations/trips
```

공통 endpoint는 `user_id`, `method`, `target`, `limit`을 받는다. W2에서 지원하는
method는 `preference_mock`뿐이고 target은 `{ "type": "place", "region_code": ... }`
또는 `{ "type": "trip", "trip_id": ... }`다. `limit`은 1~100이며 지원하지 않는
method/target 또는 target별 필수값 누락은 `422`다.

`/recommendations/places`는 place target으로, `/recommendations/trips`는 trip target으로
공통 request를 normalize해 같은 추천 계산을 수행한다. 추천은 저장하지 않는다.

응답 data에는 `method`, 원래 `target`, `fallback`, 그리고 `place_id`, `place_name`,
`category`, `score`, `rank`, `reasons`를 가진 `items`가 포함된다.

## Trip fallback

W2에서 `/recommendations/trips`와 `target.type=trip`은 trip 존재 여부와 소유자만
검증한 뒤 place 추천으로 fallback한다. 현재 dev 기준 `trips`는 `place_id`를 보유하지
않는다. W3에서 `trips.place_id`가 추가되면 `trip.place_id`를 context로 사용하는
추천으로 교체한다.

fallback 응답은 `used: true`, `reason: "trip_place_not_available"`,
`fallback_target: {"type":"place"}`를 포함한다. trip이 없거나 요청 user의 소유가
아니면 모두 `404 {"detail":"Trip not found"}`다.

## 점수 기준

- 선호 category: +50, 회피 category: -100
- 조용함 선호 시 quiet score 4 이상: +20, 2 이하: -10
- 도보 제한 이내: +20, 초과: -30
- 첫 여행자이고 초보 친화적: +15, 아니면 -15

점수 내림차순, 장소명 오름차순, place ID 오름차순으로 정렬하며 rank는 1부터 매긴다.
