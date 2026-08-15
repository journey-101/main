import pytest

from app.db import uow as uow_module


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_request_uow_commits_success(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(uow_module, "SessionLocal", lambda: session)
    monkeypatch.setattr(uow_module, "SQLAlchemyUnitOfWork", lambda value: value)
    dependency = uow_module.get_uow()
    assert next(dependency) is session
    with pytest.raises(StopIteration):
        next(dependency)
    assert session.committed and session.closed and not session.rolled_back


def test_request_uow_rolls_back_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(uow_module, "SessionLocal", lambda: session)
    monkeypatch.setattr(uow_module, "SQLAlchemyUnitOfWork", lambda value: value)
    dependency = uow_module.get_uow()
    next(dependency)
    with pytest.raises(RuntimeError):
        dependency.throw(RuntimeError("first attempt creation failed"))
    assert session.rolled_back and session.closed and not session.committed
