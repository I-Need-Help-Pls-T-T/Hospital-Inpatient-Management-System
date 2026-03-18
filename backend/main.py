import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from backend.database import engine
from backend import models

from backend.routers import (
    auth, patients, departments, positions, rooms, wards,
    staff, hospitalizations, med_entries, medication_orders,
    payments, admissions, staff_roles, admission_teams, feedback
)
from backend.admin.routers import system

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HIMS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(positions.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")
app.include_router(wards.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(hospitalizations.router, prefix="/api")
app.include_router(med_entries.router, prefix="/api")
app.include_router(medication_orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(admissions.router, prefix="/api")
app.include_router(staff_roles.router, prefix="/api")
app.include_router(admission_teams.router, prefix="/api")
app.include_router(system.router, prefix="/api/admin")
app.include_router(feedback.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
