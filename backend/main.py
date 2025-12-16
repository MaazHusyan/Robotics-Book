from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings
from src.api.root_endpoint import router as root_router
from src.api.book_content_endpoint import router as book_content_router
from src.api.health_endpoint import router as health_router
from src.api.status_endpoint import router as status_router
from src.utils.middleware import RequestLoggingMiddleware

app = FastAPI(
    title="Robotics Book API",
    description="API for accessing robotics book content",
    version="0.1.0"
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware using configuration values
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API routers
app.include_router(root_router)
app.include_router(book_content_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(status_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Robotics Book API", "status": "running", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)