from sqlalchemy import Column, Integer, String, Date, Boolean, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class GenderType(enum.Enum):
    Мужской = "Мужской"
    Женский = "Женский"

class StaffCondition(enum.Enum):
    Активен = "Активен"
    На_больничном = "На больничном"
    Отпуск = "Отпуск"
    Уволен = "Уволен"

class PaymentMethod(enum.Enum):
    Наличные = "Наличные"
    Карта = "Карта"
    Страховка = "Страховка"

# --- Справочники ---
class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    profile = Column(String(100))
    category = Column(String(100))

class Position(Base):
    __tablename__ = "position"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    med_education = Column(Boolean, default=True)
    lvl_responsibility = Column(Integer)
    description = Column(Text)

class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))
    number = Column(Integer, nullable=False)
    capacity = Column(Integer)
    department_id = Column(Integer, ForeignKey("department.id"))

    department = relationship("Department", back_populates="rooms")
    wards = relationship("Ward", back_populates="room")
    staff = relationship("Staff", back_populates="room")

class Ward(Base):
    __tablename__ = "ward"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    w_place = Column(Integer, default=0)
    m_place = Column(Integer, default=0)

    room = relationship("Room", back_populates="wards")
    hospitalizations = relationship("Hospitalization", back_populates="ward")

class StaffRole(Base):
    __tablename__ = "staff_role"

    staff_id = Column(Integer, ForeignKey("staff.id"), primary_key=True)
    position_id = Column(Integer, ForeignKey("position.id"), primary_key=True)
    appointment_date = Column(Date, primary_key=True)
    end_date = Column(Date)

    staff = relationship("Staff", back_populates="staff_roles")
    position = relationship("Position")

# --- Ввод (Добавить таблицы!!!) ---

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    condition = Column(Enum(StaffCondition), default=StaffCondition.Активен)
    room_id = Column(Integer, ForeignKey("room.id"))

    room = relationship("Room", back_populates="staff")
    staff_roles = relationship("StaffRole", back_populates="staff")
    med_entries = relationship("MedEntry", back_populates="staff")
    admission_teams = relationship("AdmissionTeam", back_populates="staff")

class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderType))
    address = Column(Text)
    passport = Column(String(50))
    phone = Column(String(20))

    hospitalizations = relationship("Hospitalization", back_populates="patient")
    med_entries = relationship("MedEntry", back_populates="patient")

class Hospitalization(Base):
    __tablename__ = "hospitalization"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.id"))
    ward_id = Column(Integer, ForeignKey("ward.id"))
    care_type = Column(String(100))
    outcome = Column(String(255))
    treatment_summary = Column(Text)
    is_paid = Column(Boolean, default=False)

    patient = relationship("Patient", back_populates="hospitalizations")
    ward = relationship("Ward", back_populates="hospitalizations")
    patient_admission = relationship("PatientAdmission", back_populates="hospitalization", uselist=False)
    admission_teams = relationship("AdmissionTeam", back_populates="hospitalization")
    payments = relationship("Payment", back_populates="hospitalization")
