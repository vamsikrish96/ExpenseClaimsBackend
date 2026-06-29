import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.error_handler import setup_error_handlers
from app.config import settings
from app.schemas.response import SuccessResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Expense Approval Workflow API",
    description="API for managing employee expense claims with approval workflow",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

setup_error_handlers(app)


@app.get("/health", tags=["health"])
async def health_check():
    return SuccessResponse(data={"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
