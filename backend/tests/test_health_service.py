from app.domains.health.service import check_database_health


class FakeResult:
    def scalar_one(self) -> int:
        return 1


class FakeSession:
    def execute(self, statement: object) -> FakeResult:
        self.statement = statement
        return FakeResult()


def test_database_health_maps_select_result() -> None:
    session = FakeSession()

    result = check_database_health(session)  # type: ignore[arg-type]

    assert result.status == "ok"
    assert result.db == "connected"
    assert result.result == 1
