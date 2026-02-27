from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.admin.routers import system
from backend.database import engine
from backend import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HIMS API",
    description="Информационная система управления стационарным лечением в больнице",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers import (
    patients, departments, positions, rooms, wards,
    staff, hospitalizations, med_entries, medication_orders,
    payments, admissions, staff_roles, admission_teams
)

app.include_router(patients.router)
app.include_router(departments.router)
app.include_router(positions.router)
app.include_router(rooms.router)
app.include_router(wards.router)
app.include_router(staff.router)
app.include_router(hospitalizations.router)
app.include_router(med_entries.router)
app.include_router(medication_orders.router)
app.include_router(payments.router)
app.include_router(admissions.router)
app.include_router(staff_roles.router)
app.include_router(admission_teams.router)
app.include_router(system.router)

@app.get("/")
async def root():
    return {
        "message": "HIMS API работает",
        "version": "1.0.0",
        "status": "OK",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Нарушение уникальности данных (например, такой паспорт уже есть)"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
