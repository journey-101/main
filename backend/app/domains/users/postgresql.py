from sqlalchemy import text
from sqlalchemy.orm import Session


class PostgreSQLUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure(self, firebase_uid: str) -> None:
        self._session.execute(
            text("""
            insert into app_users (firebase_uid) values (:uid)
            on conflict (firebase_uid) do update set updated_at = now()
        """),
            {"uid": firebase_uid},
        )
