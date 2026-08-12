# Places API 계약

검증일: 2026-08-12

기본 경로는 `/api/v1/places`다. 장소 데이터는 PostgreSQL `places`
테이블에서 조회한다.

## 장소 검색

```http
GET /api/v1/places/search
```

지원 query:

```text
q=카페
region_code=KR-41
category=cafe
lat=37.5034
lng=126.7658
radius_m=3000
limit=20
cursor=
```

- 모든 query는 선택 값이다.
- 요청 body는 사용하지 않으며 검색 조건은 URL query parameter로 전달한다.
- `lat`, `lng`, `radius_m`는 함께 전달해야 한다.
- `limit`은 `1` 이상 `100` 이하이며 기본값은 `20`이다.
- `cursor`는 계약 호환을 위해 받지만 현재 구현에서는 사용하지 않는다.
- 현재 구현은 조건에 맞는 장소를 최대 `limit`개 반환하며
  `next_cursor`는 항상 `null`이다.

응답 `data`:

```json
{
  "items": [
    {
      "id": "30000000-0000-0000-0000-000000000001",
      "provider": "mock",
      "provider_place_id": "bucheon-001",
      "name": "한국만화박물관",
      "category": "museum",
      "tags": ["indoor", "solo_friendly"],
      "address": "경기도 부천시 원미구 길주로 1",
      "region_code": "KR-41",
      "lat": 37.5088,
      "lng": 126.742,
      "price_level": 1,
      "source_url": "https://www.komacon.kr/comicsmuseum"
    }
  ],
  "next_cursor": null
}
```

## 장소 상세 조회

```http
GET /api/v1/places/{place_id}
```

목록 항목의 필드에 `opening_hours`, `phone`을 추가로 반환한다.

응답 `data`:

```json
{
  "id": "30000000-0000-0000-0000-000000000001",
  "provider": "mock",
  "provider_place_id": "bucheon-001",
  "name": "한국만화박물관",
  "category": "museum",
  "tags": ["indoor", "solo_friendly"],
  "address": "경기도 부천시 원미구 길주로 1",
  "region_code": "KR-41",
  "lat": 37.5088,
  "lng": 126.742,
  "opening_hours": {
    "summary": "10:00-18:00"
  },
  "price_level": 1,
  "phone": "032-310-3090",
  "source_url": "https://www.komacon.kr/comicsmuseum"
}
```

존재하지 않는 `place_id`면 `404 {"detail": "Place not found"}`를 반환한다.

## 검증 및 데이터 오류

- UUID 또는 query 형식이 잘못되면 `422`를 반환한다.
- DB 조회 등 처리되지 않은 서버 오류는 `500`을 반환한다. FE는 서버 오류의
  response body 형태에 의존하지 않는다.
