import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HIMS API", description="Информационная система управления стационарным лечением в больнице")

# Разрешения (поменять потом!!!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавить таблицы!!!
from routers import patients, staff, departments, admission_team

app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
#app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
#app.include_router(admission_team.router, prefix="/api/admission_team", tags=["admission_team"])

@app.get("/")
async def root():
    return {"messege": "HIMS API работает", "status": "OK"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
