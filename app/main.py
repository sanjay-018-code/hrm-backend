import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.database import check_database_connection

from routes.employee import router as employee_router
from routes.auth import router as auth_router
from routes.attendance import router as attendance_router
from routes.leave import router as leave_router
from routes.payroll import router as payroll_router
from routes.department import router as department_router
from routes.dashboard import router as dashboard_router
from routes.users import router as users_router 

app = FastAPI()
logger = logging.getLogger(__name__)


@app.exception_handler(PyMongoError)
async def database_error_handler(request: Request, error: PyMongoError):
    logger.error("MongoDB request failed: %s", error)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is temporarily unavailable"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hrm-frontend-ruddy.vercel.app",
        "https://hrm-frontend-m7xx1glcc-sanjay018.vercel.app",
        "https://hrm-frontend-c73pgefkf-sanjay018.vercel.app",
        "https://hrmanagementp.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    employee_router,
    prefix="/employees",
    tags=["Employees"]
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    attendance_router,
    prefix="/attendance",
    tags=["Attendance"]
)

app.include_router(
    leave_router,
    prefix="/leave",
    tags=["Leave"]
)

app.include_router(
    payroll_router,
    prefix="/payroll",
    tags = ["Payroll"]
)

app.include_router(
    department_router,
    prefix="/department",
    tags=["Department"]
)

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

@app.get("/")
def home():
    return "API Running"


@app.get("/health")
def health_check():
    try:
        check_database_connection()
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail="Database is temporarily unavailable",
        ) from error

    return {"status": "ok", "database": "connected"}
