# Точка входа FastAPI (создание app, подключение роутеров)
from fastapi import FastAPI
from backend.app.api.routers import (
    patients, 
    auth, 
    admission_teams, 
    staff, 
    departments, 
    rooms, 
    wards, 
    admissions,
    staff_roles,
    positions,
    hospitalizations,
    payments,
    med_entries,
    medication_orders,
    feedback,
    system
)

app = FastAPI(title="Hospital API")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(admission_teams.router)
app.include_router(staff.router)
app.include_router(departments.router)
app.include_router(rooms.router)
app.include_router(wards.router)
app.include_router(admissions.router)
app.include_router(staff_roles.router)
app.include_router(positions.router)
app.include_router(hospitalizations.router)
app.include_router(payments.router)
app.include_router(med_entries.router)
app.include_router(medication_orders.router)
app.include_router(feedback.router)
app.include_router(system.router)

@app.get("/")
def root():
    return {"message": "API is working"}