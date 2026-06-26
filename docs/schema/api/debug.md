# Debug API 계약

변경일: 2026-06-27  
변경 브랜치: `feat/14-trip`

기본 경로는 `/api/v1/debug`다.

## Test User 조회

```http
GET /api/v1/debug/test-user
```

고정된 개발/검증용 사용자 ID를 반환한다.

응답:

```json
{
  "success": true,
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000000"
  }
}
```
