# Health API 계약

검증일: 2026-08-12

기본 경로는 `/api/v1/health`다.

## 서비스 상태 조회

```http
GET /api/v1/health
```

응답:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "backend"
  }
}
```

## DB 상태 조회

```http
GET /api/v1/health/db
```

응답:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "db": "connected",
    "result": 1
  }
}
```

DB 연결 확인에 실패하면 공통 에러 응답을 반환한다.

```json
{
  "success": false,
  "error": {
    "code": "DB_CONNECTION_FAILED",
    "message": "Database connection failed"
  }
}
```
