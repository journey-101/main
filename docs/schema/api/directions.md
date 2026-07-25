# Directions API 계약

변경일: 2026-07-25
변경 브랜치: `feat/29-directions`

기본 경로는 `/api/v1/directions`다. 프론트가 전달한 출발지 좌표와 Place DB의
목적지 좌표를 이용해 경로를 검색한다.

현재 구현은 외부 길찾기 공급자 연동 전의 Mock 구현이다. 두 좌표 사이의 직선
거리와 이동 수단별 평균 속도로 예상 시간을 계산한다. 응답 계약은 실제 공급자
연동 후에도 유지한다.

## 경로 검색

```http
POST /api/v1/directions/search
Content-Type: application/json
```

요청:

```json
{
  "place_id": "30000000-0000-0000-0000-000000000001",
  "origin": {
    "latitude": 37.5034,
    "longitude": 126.766
  },
  "mode": "walking"
}
```

- `place_id`는 Places API에서 선택한 장소 ID다.
- `origin`은 프론트가 GPS 또는 개발용 Mock으로 제공한다.
- 백엔드는 `place_id`로 목적지 이름과 좌표를 조회한다.
- `mode`는 `walking`, `driving`, `transit` 중 하나다.
- 좌표계는 WGS84다.
- 요청 body의 추가 필드는 허용하지 않는다.

응답 `data`:

```json
{
  "routes": [
    {
      "provider": "mock",
      "mode": "walking",
      "origin": {
        "latitude": 37.5034,
        "longitude": 126.766,
        "place_id": null,
        "name": null
      },
      "destination": {
        "latitude": 37.5088,
        "longitude": 126.742,
        "place_id": "30000000-0000-0000-0000-000000000001",
        "name": "한국만화박물관"
      },
      "summary": {
        "distance_meters": 2200,
        "duration_seconds": 1833
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [126.766, 37.5034],
          [126.742, 37.5088]
        ]
      }
    }
  ]
}
```

- 거리 단위는 meter, 시간 단위는 second다.
- `geometry`는 GeoJSON `LineString`이며 좌표 순서는 `[longitude, latitude]`다.
- 현재 `provider`는 `mock`이다.

## 오류

- 존재하지 않는 `place_id`: `404 {"detail": "Place not found"}`
- 잘못된 UUID, 좌표, 이동 수단 또는 추가 필드: `422`
- Place DB 조회 실패: `500 {"detail": "Unknown place data error"}`

외부 공급자를 연동할 때 timeout, 쿼터 초과, 공급자 장애에 대한 오류 계약을
추가한다.
