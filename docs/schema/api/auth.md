# Authentication API

Firebase Authentication is the account authority. Protected endpoints accept only a
Firebase ID token; a caller cannot select a user with a query or body field.

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

Missing, malformed, expired, or revoked tokens return `401`. The same header is
required by trips, preferences, and recommendation endpoints. Places and health
remain public. The backend follows Firebase's
[ID-token verification flow](https://firebase.google.com/docs/auth/admin/verify-id-tokens).

The first authenticated request creates or refreshes an `app_users` projection.
This row exists only for SQL foreign keys; Firebase remains the account ledger.
