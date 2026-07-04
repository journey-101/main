# Places API 계약

변경일: 2026-07-05  
변경 브랜치: `feat/13-place_basic`

기본 경로는 `/api/v1/places`다. 현재 구현은 JSON 목업 데이터 파일을
읽어 장소 목록과 상세 정보를 반환한다.

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
- `lat`, `lng`, `radius_m`는 함께 전달해야 한다.
- `limit`은 `1` 이상 `100` 이하이며 기본값은 `20`이다.
- `cursor`는 계약 호환을 위해 받지만 목업 구현에서는 사용하지 않는다.

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
- 목업 파일을 읽거나 검증할 수 없으면
  `500 {"detail": "Unknown place data error"}`를 반환한다.
