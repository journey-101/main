# Authentication API 계약

변경일: 2026-08-12

Firebase Authentication이 사용자 계정의 기준이다. 인증 API는 Firebase ID
토큰만 신뢰하며, 호출자가 query나 body의 `user_id`로 사용자를 선택할 수 없다.

## 현재 사용자 조회

```http
GET /api/v1/auth/me
Authorization: Bearer <firebase-id-token>
```

```json
{
  "success": true,
  "data": {
    "uid": "firebase-uid",
    "email": "user@example.com",
    "name": "User",
    "provider": "google.com"
  }
}
```

토큰이 없거나 잘못됐거나 만료·취소된 경우 `401`을 반환한다. 같은 헤더가 trips,
preferences, recommendations API에도 필요하다. Places, directions, health는
공개 API다.

FE는 로그인 후 얻은 ID 토큰을 인증 API 요청마다 다음과 같이 전달한다.

```ts
const token = await firebaseUser.getIdToken();

await fetch("/api/v1/trips", {
  headers: { Authorization: `Bearer ${token}` },
});
```

토큰 문자열을 사용자 ID처럼 저장하거나 `user_id` 필드로 복사하지 않는다. SDK가
필요할 때 갱신한 ID 토큰을 요청 헤더에 넣는다.

첫 인증 요청은 SQL 외래 키에 필요한 `app_users` projection을 자동으로 보장한다.
FE가 별도의 사용자 생성 API를 호출할 필요는 없다.
