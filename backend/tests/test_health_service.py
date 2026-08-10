from app.domains.health.service import check_database_health


class FakeSession:
    def ping(self) -> int:
        return 1


def test_database_health_maps_select_result() -> None:
    session = FakeSession()

    result = check_database_health(session)  # type: ignore[arg-type]

    assert result.status == "ok"
    assert result.db == "connected"
    assert result.result == 1
