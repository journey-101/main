# Directions API 계약

변경일: 2026-07-25
변경 브랜치: `feat/29-directions`

기본 경로는 `/api/v1/directions`다. 프론트가 전달한 출발지 좌표와 Place DB의
목적지 좌표를 이용해 경로를 검색한다.

현재 구현은 외부 길찾기 공급자 연동 전의 Mock 구현이다. 두 좌표 사이의 직선
거리와 이동 수단별 평균 속도로 예상 시간을 계산하고, 지도 표시를 검증할 수
있도록 꺾이는 Mock 경로 좌표를 반환한다. 응답 계약은 실제 공급자 연동 후에도
유지한다.

공급자는 `DIRECTIONS_PROVIDER` 환경변수로 선택한다. 현재는 `mock`만 구현되어
있으며 `odsay` 설정과 API 호출 구현은 후속 작업에서 추가한다.

## 프론트엔드 계약

프론트엔드는 공급자별 응답이나 `mapObj`, `loadLane`을 알 필요가 없다. 장소가
선택되면 이 API에 출발 좌표, 목적지 `place_id`, 이동 수단을 전달하고 다음 값만
사용한다.

- `origin`, `destination`: 출발지와 DB에서 조회한 목적지 정보
- `summary.distance_meters`: 경로 전체 길이(meter)
- `summary.duration_seconds`: 예상 소요 시간(second)
- `geometry.coordinates`: 지도에 순서대로 그릴 전체 경로 좌표

Mock과 ODsay 공급자는 같은 응답을 반환한다. 향후 ODsay 연동 시 백엔드가
`searchPubTransPathT`와 `loadLane` 결과를 위 필드로 변환하므로 프론트 계약은
변경하지 않는다. `routes`는 후보 경로 배열이며 프론트는 기본적으로 첫 번째
경로를 표시할 수 있다.

Mock 공급자 내부 흐름도 실제 ODsay와 동일한 두 단계로 구성한다.

1. `searchPubTransPathT` 형태의 호출로 `result.path[].info` 안의
   `totalDistance`, 분 단위 `totalTime`, `mapObj`를 받는다.
2. 각 경로의 `mapObj` 앞에 기준점 `0:0@`를 붙여 `loadLane`의 `mapObject`로
   전달하고
   `result.lane[].section[].graphPos[]`의 `{x, y}` 좌표를 받는다.
3. 백엔드가 분을 초로 변환하고 `{x, y}`를 `[longitude, latitude]`로 변환해
   아래 공통 응답을 만든다.

Mock ODsay client는 HTTP 통신만 생략하며 호출 순서와 원본 JSON 구조는 위 형식을
따른다. 실제 연동 시 이 client를 HTTP 구현으로 교체하고 변환 계층은 유지한다.

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
  "mode": "transit"
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
      "mode": "transit",
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
        "distance_meters": 2490,
        "duration_seconds": 480
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [126.766, 37.5034],
          [126.7576, 37.50394],
          [126.7576, 37.50691],
          [126.748, 37.50691],
          [126.742, 37.5088]
        ]
      }
    }
  ]
}
```

- 거리 단위는 meter, 시간 단위는 second이며 두 값은 0 이상이다.
- `geometry`는 GeoJSON `LineString`이며 좌표 순서는 `[longitude, latitude]`다.
- `geometry.coordinates`는 출발점과 도착점을 포함하며 최소 2개다.
- Mock 좌표는 ODsay `loadLane` 응답을 연결한 폴리라인처럼 중간 꺾임점을 포함한다.
- 현재 `provider`는 `mock`이다.

## 오류

- 존재하지 않는 `place_id`: `404 {"detail": "Place not found"}`
- 잘못된 UUID, 좌표, 이동 수단 또는 추가 필드: `422`
- Place DB 조회 실패: `500 {"detail": "Unknown place data error"}`

외부 공급자를 연동할 때 timeout, 쿼터 초과, 공급자 장애에 대한 오류 계약을
추가한다.
