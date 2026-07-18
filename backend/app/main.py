from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.errors import DatabaseConnectionError

settings = get_settings()
app = FastAPI(title="Journey101 Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type"],
)
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
