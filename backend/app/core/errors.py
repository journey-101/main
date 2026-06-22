from fastapi import HTTPException, status


class DatabaseConnectionError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "DB_CONNECTION_FAILED",
                "message": "Database connection failed",
            },
        )
