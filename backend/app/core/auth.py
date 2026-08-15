from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Protocol

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.core.config import get_settings
from app.db.uow import UnitOfWork, get_uow


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str | None = None
    name: str | None = None
    provider: str | None = None


class TokenVerifier(Protocol):
    def verify(self, token: str) -> CurrentUser: ...


class FirebaseTokenVerifier:
    def __init__(self) -> None:
        try:
            self._app = firebase_admin.get_app()
        except ValueError:
            self._app = firebase_admin.initialize_app(
                options={"projectId": get_settings().google_cloud_project}
            )

    def verify(self, token: str) -> CurrentUser:
        try:
            claims = auth.verify_id_token(token, app=self._app, check_revoked=True)
        except Exception as exc:
            raise _unauthorized() from exc
        firebase_claims = claims.get("firebase") or {}
        return CurrentUser(
            uid=claims["uid"],
            email=claims.get("email"),
            name=claims.get("name"),
            provider=firebase_claims.get("sign_in_provider"),
        )


@lru_cache
def get_token_verifier() -> TokenVerifier:
    return FirebaseTokenVerifier()


bearer_scheme = HTTPBearer(auto_error=False)


def verify_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()
    return verifier.verify(credentials.credentials)


def get_current_user(
    user: Annotated[CurrentUser, Depends(verify_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> CurrentUser:
    uow.users.ensure(user.uid)
    return user


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing Firebase ID token",
        headers={"WWW-Authenticate": "Bearer"},
    )
