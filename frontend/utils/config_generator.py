# frontend/utils/config_generator.py

from sqlalchemy import Enum as SqlaEnum, Boolean, Date, DateTime, Integer, Numeric
# Импортируйте Base и все модели из вашего файла!
from backend.app.models.base_models import Base 

def generate_table_configs():
    configs = {}
    
    # Маппинг названий таблиц БД к названиям ключей/endpoints в GUI
    endpoint_mapping = {
        "department": "departments",
        "position": "positions",
        "room": "rooms",
        "ward": "wards",
        "staff_role": "staff_roles",
        "staff": "staff",
        "patient": "patients",
        "hospitalization": "hospitalizations",
        "patient_admission": "admissions",
        "admission_team": "admission_teams",
        "med_entry": "med_entries",
        "medication_order": "medication_orders",
        "payment": "payments",
        "feedback": "feedback"
    }

    # Перебираем все модели, которые наследуются от Base
    for model in Base.__subclasses__():
        tablename = getattr(model, "__tablename__", None)
        if not tablename:
            continue
            
        endpoint = endpoint_mapping.get(tablename, tablename + "s")
        fields = []

        for col in model.__table__.columns:
            # 1. Пропускаем первичные ключи-автоинкременты и системные поля
            if col.name == "id" and col.primary_key:
                continue
            if col.name == "created_at":
                continue

            # 2. Формируем базовый label
            label = col.name.replace("_", " ").capitalize()
            field_def = {"name": col.name, "label": label, "type": "text"}

            # 3. Проверка на обязательность (nullable)
            if col.nullable or col.default is not None:
                field_def["label"] += " (опц.)"
            else:
                field_def["label"] += "*"

            # 4. Определение типа поля для GUI
            col_type = type(col.type)
            
            # Особое поле для паролей
            if col.name == "password_hash" or col.name == "password":
                field_def["name"] = "password"  # Адаптируем под API
                field_def["type"] = "password"
                
            elif issubclass(col_type, Date):
                field_def["type"] = "date"
                
            elif issubclass(col_type, DateTime) or col_type.__name__ == 'TIMESTAMP':
                field_def["label"] += " (YYYY-MM-DD HH:MM)"
                
            elif issubclass(col_type, Integer) or issubclass(col_type, Numeric):
                if col.foreign_keys:
                    field_def["label"] += " [ID]"
                else:
                    field_def["label"] += " [число]"
                    
            elif issubclass(col_type, Boolean):
                field_def["type"] = "boolean"
                
            elif issubclass(col_type, SqlaEnum):
                field_def["type"] = "enum"
                # Вытаскиваем значения из Python Enum
                field_def["choices"] = [e.value for e in col.type.enum_class]

            fields.append(field_def)
            
        configs[endpoint] = fields

    return configs