from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.employees import employee_error_handler
from app.routers.employees import router as employees_router
from app.routers.health import router as health_router
from app.routers.insights import router as insights_router
from app.services.errors import EmployeeError

app = FastAPI(title=settings.app_name)
app.exception_handler(EmployeeError)(employee_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(employees_router)
app.include_router(insights_router)
