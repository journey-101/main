from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.core.errors import DatabaseConnectionError

app = FastAPI(title="Journey101 Backend")
app.include_router(api_router)


@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(
    request: Request,
    exc: DatabaseConnectionError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )
