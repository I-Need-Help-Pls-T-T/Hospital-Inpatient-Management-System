from sqlalchemy import Column, Integer, String, Date, Boolean, Text, Numeric, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from backend.app.database import Base
import enum
from datetime import datetime

# ----- Перечисления (ENUM) -----
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

# ----- Справочные таблицы (LookUp Tables) -----
class Department(Base):
    """
    Отделение больницы
    Права: только суперпользователь может изменять
    """
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    profile = Column(String(100))
    category = Column(String(100))

    # Связи
    rooms = relationship("Room", back_populates="department", cascade="all, delete")

class Position(Base):
    """
    Должность
    Права: только суперпользователь может изменять
    """
    __tablename__ = "position"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    med_education = Column(Boolean, default=True)
    description = Column(Text)

    # Связи
    staff_roles = relationship("StaffRole", back_populates="position", cascade="all, delete")

class Room(Base):
    """
    Помещение (кабинет)
    Права: только суперпользователь может изменять
    """
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100))
    number = Column(Integer, nullable=False)
    capacity = Column(Integer)
    department_id = Column(Integer, ForeignKey("department.id", ondelete="CASCADE"))

    # Связи
    department = relationship("Department", back_populates="rooms")
    wards = relationship("Ward", back_populates="room")
    staff = relationship("Staff", back_populates="room")


class Ward(Base):
    """
    Палата (детализация помещения)
    Права: только суперпользователь может изменять
    """
    __tablename__ = "ward"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id", ondelete="CASCADE"))
    w_place = Column(Integer, default=0)
    m_place = Column(Integer, default=0)

    # Связи
    room = relationship("Room", back_populates="wards")
    hospitalizations = relationship("Hospitalization", back_populates="ward")


class StaffRole(Base):
    """
    Связь сотрудника с должностью (история назначений)
    Права: только суперпользователь может изменять
    """
    __tablename__ = "staff_role"

    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), primary_key=True)
    position_id = Column(Integer, ForeignKey("position.id", ondelete="CASCADE"), primary_key=True)
    appointment_date = Column(Date, primary_key=True)
    end_date = Column(Date)

    # Связи
    staff = relationship("Staff", back_populates="staff_roles")
    position = relationship("Position", back_populates="staff_roles")


# ----- Основные таблицы (Operational Tables) -----
class Staff(Base):
    """
    Сотрудник (персонал)
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    condition = Column(Enum(StaffCondition), default=StaffCondition.Активен)
    room_id = Column(Integer, ForeignKey("room.id", ondelete="SET NULL"))
    login = Column(String(50), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    access_level = Column(Integer, default=0)

    # Связи
    room = relationship("Room", back_populates="staff")
    staff_roles = relationship("StaffRole", back_populates="staff", cascade="all, delete")
    med_entries = relationship("MedEntry", back_populates="staff", cascade="all, delete")

class Patient(Base):
    """
    Пациент (центральная таблица, стартовый экран)
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderType))
    address = Column(Text)
    passport = Column(String(50), unique=True)
    phone = Column(String(20))

    # Связи
    hospitalizations = relationship("Hospitalization", back_populates="patient", cascade="all, delete")
    med_entries = relationship("MedEntry", back_populates="patient", cascade="all, delete")

class Hospitalization(Base):
    """
    Госпитализация
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "hospitalization"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.id", ondelete="CASCADE"))
    ward_id = Column(Integer, ForeignKey("ward.id", ondelete="SET NULL"))
    care_type = Column(String(100))
    outcome = Column(String(255))
    treatment_summary = Column(Text)

    # Связи
    patient = relationship("Patient", back_populates="hospitalizations")
    ward = relationship("Ward", back_populates="hospitalizations")
    patient_admission = relationship("PatientAdmission", back_populates="hospitalization", uselist=False, cascade="all, delete")
    payments = relationship("Payment", back_populates="hospitalization", cascade="all, delete")
    admission_team = relationship("AdmissionTeam", back_populates="hospitalization", cascade="all, delete")

    @property
    def is_paid(self):
        return len(self.payments) > 0


class PatientAdmission(Base):
    """
    Время поступления и выбытия пациента
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "patient_admission"

    hospitalization_id = Column(Integer, ForeignKey("hospitalization.id", ondelete="CASCADE"), primary_key=True)
    arrival_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)

    # Связи
    hospitalization = relationship("Hospitalization", back_populates="patient_admission")


class AdmissionTeam(Base):
    """
    Состав медицинской бригады
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "admission_team"

    id = Column(Integer, primary_key=True, index=True)
    hospitalization_id = Column(Integer, ForeignKey("hospitalization.id", ondelete="CASCADE"))
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"))
    begin_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    role = Column(String(200))

    # Связи
    hospitalization = relationship("Hospitalization", back_populates="admission_team")
    staff = relationship("Staff")


class MedEntry(Base):
    """
    Запись в истории болезни
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "med_entry"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.id", ondelete="CASCADE"))
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"))
    entry_date = Column(TIMESTAMP, default=datetime.now)
    description = Column(Text)

    # Связи
    patient = relationship("Patient", back_populates="med_entries")
    staff = relationship("Staff", back_populates="med_entries")
    medication_orders = relationship("MedicationOrder", back_populates="med_entry", cascade="all, delete")

class MedicationOrder(Base):
    """
    Лист назначения
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "medication_order"

    id = Column(Integer, primary_key=True, index=True)
    med_entry_id = Column(Integer, ForeignKey("med_entry.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    dose = Column(String(100))
    rules_taking = Column(Text)
    begin_date = Column(Date)
    end_date = Column(Date)

    # Связи
    med_entry = relationship("MedEntry", back_populates="medication_orders")


class Payment(Base):
    """
    Оплата
    Права: пользователь может просматривать и редактировать
    """
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    hospitalization_id = Column(Integer, ForeignKey("hospitalization.id", ondelete="CASCADE"), unique=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(Enum(PaymentMethod))

    # Связи
    hospitalization = relationship("Hospitalization", back_populates="payments")

class FeedbackType(enum.Enum):
    Ошибка = "Ошибка"
    Предложение = "Предложение"
    Вопрос = "Вопрос"

class Feedback(Base):
    """
    Обратная связь / сообщения об ошибках от пользователей
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    feedback_type = Column(Enum(FeedbackType), default=FeedbackType.Ошибка)
    section = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.now)
    is_read = Column(Boolean, default=False)

    # Связи
    staff = relationship("Staff")
