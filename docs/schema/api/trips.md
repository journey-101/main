# Trips API 계약

변경일: 2026-06-27  
변경 브랜치: `feat/14-trip`

기본 경로는 `/api/v1/trips`다.

## 공통 타입

Attempt `status`는 아래 값만 허용한다.

```text
started, completed, aborted
```

성공 응답은 아래 형태를 사용한다.

```json
{
  "success": true,
  "data": {}
}
```

## Trip 목록 조회

```http
GET /api/v1/trips?user_id={user_id}
```

응답 `data`:

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "current_attempt": {
      "id": "uuid",
      "status": "started",
      "feedback_text": null
    }
  }
]
```

`current_attempt`는 `created_at desc, id desc` 기준 가장 최근 attempt다.

## Trip 생성

```http
POST /api/v1/trips
Content-Type: application/json

{
  "user_id": "uuid",
  "title": "string"
}
```

Trip을 생성하고 `status: "started"`인 기본 attempt도 함께 생성한다.

응답 `data`:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "current_attempt": {
    "id": "uuid",
    "status": "started",
    "feedback_text": null
  }
}
```

존재하지 않는 `user_id`면 `404 {"detail": "User not found"}`를 반환한다.

## Trip 상세 조회

```http
GET /api/v1/trips/{trip_id}
```

응답 `data`:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "attempts": [
    {
      "id": "uuid",
      "trip_id": "uuid",
      "status": "started",
      "feedback_text": null,
      "created_at": "datetime"
    }
  ]
}
```

존재하지 않는 `trip_id`면 `404 {"detail": "Trip not found"}`를 반환한다.

## Trip 수정

```http
PATCH /api/v1/trips/{trip_id}
Content-Type: application/json

{
  "title": "string"
}
```

`title`만 허용한다.

응답 `data`:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "current_attempt": {
    "id": "uuid",
    "status": "started",
    "feedback_text": null
  }
}
```

## Attempt 생성

```http
POST /api/v1/trips/{trip_id}/attempts
Content-Type: application/json

{
  "status": "started"
}
```

`status`는 선택 값이며 생략하면 `started`를 사용한다.

응답 `data`:

```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "status": "started",
  "feedback_text": null
}
```

존재하지 않는 `trip_id`면 `404 {"detail": "Trip not found"}`를 반환한다.

## Attempt 수정

```http
PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}
Content-Type: application/json

{
  "status": "completed",
  "feedback_text": "string"
}
```

테스트/관리 목적의 attempt 수정용 엔드포인트다. `status` 또는 `feedback_text` 중 하나 이상이 필요하다.

응답 `data`:

```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "status": "completed",
  "feedback_text": "string"
}
```

존재하지 않는 attempt 또는 다른 trip 소속 attempt면 `404 {"detail": "Trip attempt not found"}`를 반환한다.

## Attempt Feedback 수정

```http
PATCH /api/v1/trips/{trip_id}/attempts/{attempt_id}/feedback
Content-Type: application/json

{
  "feedback_text": "string"
}
```

사용자 후기 수정용 엔드포인트다. `feedback_text`만 허용한다.

응답 `data`:

```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "status": "started",
  "feedback_text": "string"
}
```

존재하지 않는 attempt 또는 다른 trip 소속 attempt면 `404 {"detail": "Trip attempt not found"}`를 반환한다.

## 검증 에러

아래 경우에는 `422`를 반환한다.

- UUID 형식이 잘못됨
- 허용하지 않는 `status` 값
- 필수 필드 누락
- strict request body의 추가 필드
- attempt 수정 요청에서 `status`, `feedback_text`가 모두 누락됨
