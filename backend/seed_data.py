import sys
import os
import random
from datetime import datetime, date, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from passlib.context import CryptContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models
from backend.database import SessionLocal, engine, Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake = Faker('ru_RU')
random.seed(42)

# ──────────────────────────────────────────────
# Справочные данные
# ──────────────────────────────────────────────

DEPARTMENTS = [
    ("Терапевтическое отделение",   "Терапия",        "Общая"),
    ("Хирургическое отделение",     "Хирургия",       "Высшая"),
    ("Кардиологическое отделение",  "Кардиология",    "Высшая"),
    ("Неврологическое отделение",   "Неврология",     "Высшая"),
    ("Реанимация и интенсив. терап","Реанимация",     "Высшая"),
]

POSITIONS = [
    ("Врач-терапевт",           True,  "Первичный приём, ведение пациентов"),
    ("Врач-хирург",             True,  "Оперативное лечение"),
    ("Врач-кардиолог",          True,  "Диагностика и лечение сердечно-сосудистых заболеваний"),
    ("Врач-невролог",           True,  "Диагностика заболеваний нервной системы"),
    ("Врач-реаниматолог",       True,  "Интенсивная терапия, реанимация"),
    ("Старшая медсестра",       True,  "Организация сестринского ухода"),
    ("Медицинская сестра",      True,  "Выполнение назначений врача, уход за пациентами"),
    ("Санитар",                 False, "Вспомогательный медицинский персонал"),
    ("Заведующий отделением",   True,  "Руководство отделением, контроль лечения"),
    ("Регистратор",             False, "Оформление документов, приём пациентов"),
]

ROOM_TYPES = ["Процедурный кабинет", "Палата", "Ординаторская", "Перевязочная", "Смотровой кабинет"]

CARE_TYPES = ["Плановая", "Экстренная", "Срочная", "Неотложная"]

OUTCOMES = [
    "Выписан (выздоровление)",
    "Выписан (с улучшением)",
    "Выписан (с ухудшением)",
    "Переведён на амбулаторное лечение",
    "Переведён в другой стационар",
    "Переведён с диагностической целью",
    "Переведён на консультацию",
    "Лечение продолжается",
]

DIAGNOSES_AND_TREATMENTS = [
    ("Острый бронхит",
     "Антибактериальная терапия, муколитики, бронходилататоры. Физиотерапия.",
     [("Амоксиклав",  "500 мг", "Внутрь 2 раза в день во время еды", 7),
      ("АЦЦ",         "600 мг", "Растворить в воде, принимать 1 раз в сутки", 10),
      ("Беродуал",    "2 дозы", "Ингаляции 3 раза в день", 7)]),

    ("Гипертоническая болезнь II стадии",
     "Гипотензивная терапия, ограничение соли. ЭКГ-контроль.",
     [("Эналаприл",   "10 мг",  "Внутрь 1 раз в сутки утром", 30),
      ("Амлодипин",   "5 мг",   "Внутрь 1 раз в сутки", 30),
      ("Аспирин",     "100 мг", "Внутрь 1 раз в день после еды", 30)]),

    ("Острый аппендицит",
     "Экстренная аппендэктомия. Послеоперационная антибиотикотерапия.",
     [("Цефтриаксон", "1 г",    "Внутривенно 2 раза в сутки", 5),
      ("Метронидазол","500 мг", "Внутривенно капельно 3 раза в сутки", 5),
      ("Кетопрофен",  "100 мг", "Внутримышечно при болях", 3)]),

    ("Ишемическая болезнь сердца",
     "Антиангинальная терапия, антиагреганты. Коронарография.",
     [("Нитроглицерин","0.5 мг","Сублингвально при болях", 14),
      ("Метопролол",  "50 мг",  "Внутрь 2 раза в сутки", 30),
      ("Клопидогрел", "75 мг",  "Внутрь 1 раз в сутки", 30)]),

    ("ОНМК (ишемический инсульт)",
     "Тромболитическая терапия. Нейропротекция. Ранняя реабилитация.",
     [("Актилизе",    "0.9 мг/кг","Внутривенно (болюс + инфузия)", 1),
      ("Цитиколин",  "1000 мг", "Внутривенно капельно 1 раз в сутки", 10),
      ("Гепарин",    "5000 ЕД", "Подкожно 4 раза в сутки", 7)]),

    ("Пневмония внебольничная",
     "Антибактериальная и противовоспалительная терапия. Оксигенотерапия.",
     [("Левофлоксацин","500 мг","Внутривенно 1 раз в сутки", 7),
      ("Дексаметазон","8 мг",  "Внутривенно 1 раз в сутки", 3),
      ("Эуфиллин",   "10 мл",  "Внутривенно капельно при необходимости", 5)]),

    ("Сахарный диабет 2 типа (декомпенсация)",
     "Коррекция гипергликемии. Инсулинотерапия. Диета.",
     [("Инсулин Новорапид","8 ЕД","Подкожно перед каждым приёмом пищи", 14),
      ("Метформин",  "1000 мг","Внутрь 2 раза в день во время еды", 30),
      ("Омепразол",  "20 мг",  "Внутрь 1 раз в сутки натощак", 14)]),

    ("Желчнокаменная болезнь",
     "Лапароскопическая холецистэктомия. Спазмолитики в предоперационном периоде.",
     [("Но-шпа",     "40 мг",  "Внутримышечно 3 раза в сутки", 3),
      ("Цефазолин",  "1 г",    "Внутривенно за 30 мин до операции", 1),
      ("Кетопрофен", "100 мг", "Внутримышечно 2 раза в сутки", 3)]),
]

ADMISSION_ROLES = [
    "Лечащий врач",
    "Дежурный врач",
    "Анестезиолог",
    "Хирург",
    "Медсестра приёмного покоя",
    "Медсестра-анестезист",
    "Транспортировка пациента",
]

FEEDBACK_SUBJECTS = [
    ("Ошибка",      "Не отображаются данные в разделе «Госпитализации»",
                    "При открытии раздела таблица остаётся пустой, хотя записи точно есть. Проблема воспроизводится стабильно."),
    ("Ошибка",      "Невозможно сохранить нового пациента",
                    "При нажатии «Сохранить» в диалоге добавления пациента появляется ошибка сервера 500. Поле «Паспорт» заполнено корректно."),
    ("Предложение", "Добавить фильтрацию по дате в таблицу госпитализаций",
                    "Было бы удобно фильтровать госпитализации по диапазону дат поступления. Сейчас приходится листать вручную."),
    ("Предложение", "Экспорт данных в Excel",
                    "Нужна возможность выгрузки любой таблицы в .xlsx для последующей отчётности."),
    ("Вопрос",      "Как восстановить удалённую запись?",
                    "Случайно удалил запись в разделе «Персонал». Есть ли возможность отмены или восстановления из резервной копии?"),
    ("Ошибка",      "Поиск не находит записи по кириллице",
                    "Функция поиска не реагирует на кириллические запросы. Поиск латиницей работает нормально."),
]


# ──────────────────────────────────────────────
# Основная функция генерации
# ──────────────────────────────────────────────

def seed_all(db: Session):
    print("🧹 Очистка старых данных...")
    for table in [
        models.Feedback, models.Payment, models.MedicationOrder, models.MedEntry,
        models.AdmissionTeam, models.PatientAdmission, models.Hospitalization,
        models.StaffRole, models.Staff, models.Patient,
        models.Ward, models.Room, models.Position, models.Department,
    ]:
        db.query(table).delete()
    db.commit()

    # ── 1. Отделения ──────────────────────────────
    print("🏥 Создание отделений...")
    depts = []
    for name, profile, category in DEPARTMENTS:
        d = models.Department(
            name=name,
            phone=fake.phone_number()[:20],
            profile=profile,
            category=category,
        )
        db.add(d)
        depts.append(d)
    db.flush()

    # ── 2. Должности ──────────────────────────────
    print("📋 Создание должностей...")
    positions = []
    for name, med_edu, desc in POSITIONS:
        p = models.Position(name=name, med_education=med_edu, description=desc)
        db.add(p)
        positions.append(p)
    db.flush()

    # ── 3. Помещения и Палаты ─────────────────────
    print("🚪 Создание помещений и палат...")
    rooms = []
    wards = []
    room_number = 101
    for dept in depts:
        for i in range(3):
            room = models.Room(
                number=room_number,
                type=ROOM_TYPES[i % len(ROOM_TYPES)],
                capacity=random.choice([2, 3, 4, 6]),
                department_id=dept.id,
            )
            db.add(room)
            db.flush()
            rooms.append(room)
            room_number += 1

            # Палата только для комнат типа «Палата» и первой по счёту
            if i < 2:
                ward = models.Ward(
                    room_id=room.id,
                    w_place=random.randint(1, 3),
                    m_place=random.randint(1, 3),
                )
                db.add(ward)
                wards.append(ward)
    db.flush()

    # ── 4. Персонал ───────────────────────────────
    print("👨‍⚕️ Создание персонала...")
    staff_list = []

    # Администратор
    admin = models.Staff(
        full_name="Администратор Системы",
        phone="88005553535",
        email="admin@hospital.ru",
        login="admin",
        password_hash=pwd_context.hash("admin"),
        access_level=3,
        condition=models.StaffCondition.Активен,
        room_id=rooms[0].id,
    )
    db.add(admin)
    staff_list.append(admin)

    # Врачи по отделениям
    doctor_positions = [p for p in positions if "Врач" in p.name or "Заведующий" in p.name]
    nurse_positions  = [p for p in positions if "сестра" in p.name or "Санитар" in p.name or "Регистратор" in p.name]

    for dept_idx, dept in enumerate(depts):
        dept_rooms = [r for r in rooms if r.department_id == dept.id]

        # 2 врача на отделение
        for _ in range(2):
            s = models.Staff(
                full_name=fake.name(),
                phone=fake.phone_number()[:20],
                email=fake.email(),
                login=fake.user_name() + str(random.randint(10, 99)),
                password_hash=pwd_context.hash("1"),
                access_level=2,
                condition=models.StaffCondition.Активен,
                room_id=random.choice(dept_rooms).id,
            )
            db.add(s)
            staff_list.append(s)

        # 1 медсестра на отделение
        s = models.Staff(
            full_name=fake.name(),
            phone=fake.phone_number()[:20],
            email=fake.email(),
            login=fake.user_name() + str(random.randint(10, 99)),
            password_hash=pwd_context.hash("1"),
            access_level=1,
            condition=random.choice([
                models.StaffCondition.Активен,
                models.StaffCondition.Активен,
                models.StaffCondition.На_больничном,
                models.StaffCondition.Отпуск,
            ]),
            room_id=random.choice(dept_rooms).id,
        )
        db.add(s)
        staff_list.append(s)

    db.flush()

    # ── 5. Назначение должностей (StaffRole) ──────
    print("🗂️ Назначение должностей...")
    for s in staff_list:
        if s.access_level == 3:
            pos = next((p for p in positions if "Заведующий" in p.name), positions[0])
        elif s.access_level == 2:
            pos = random.choice(doctor_positions)
        else:
            pos = random.choice(nurse_positions)

        start = date.today() - timedelta(days=random.randint(180, 1800))
        db.add(models.StaffRole(
            staff_id=s.id,
            position_id=pos.id,
            appointment_date=start,
            end_date=None,
        ))
    db.flush()

    # ── 6. Пациенты ───────────────────────────────
    print("🧑‍⚕️ Создание пациентов...")
    patients = []
    for _ in range(30):
        p = models.Patient(
            full_name=fake.name(),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=85),
            gender=random.choice(list(models.GenderType)),
            address=fake.address().replace("\n", ", "),
            passport=fake.bothify(text='#### ######'),
            phone=fake.phone_number()[:20],
        )
        db.add(p)
        patients.append(p)
    db.flush()

    # ── 7. Госпитализации и всё связанное ─────────
    print("🏨 Оформление госпитализаций...")
    active_staff = [s for s in staff_list if s.condition == models.StaffCondition.Активен]

    for patient in patients:
        # Случайный диагноз
        diag_name, treatment_summary, medications = random.choice(DIAGNOSES_AND_TREATMENTS)

        arrival = datetime.now() - timedelta(days=random.randint(1, 30))
        is_discharged = random.random() < 0.4   # 40% выписаны
        outcome = random.choice(OUTCOMES[:7]) if is_discharged else "Лечение продолжается"
        end_time = arrival + timedelta(days=random.randint(5, 20)) if is_discharged else None

        hosp = models.Hospitalization(
            patient_id=patient.id,
            ward_id=random.choice(wards).id,
            care_type=random.choice(CARE_TYPES),
            outcome=outcome,
            treatment_summary=treatment_summary,
        )
        db.add(hosp)
        db.flush()

        # Время поступления / выбытия
        db.add(models.PatientAdmission(
            hospitalization_id=hosp.id,
            arrival_time=arrival,
            end_time=end_time,
        ))

        # Бригада (2–3 сотрудника)
        team_size = random.randint(2, 3)
        team_members = random.sample(active_staff, min(team_size, len(active_staff)))
        used_roles = []
        for member in team_members:
            role = random.choice([r for r in ADMISSION_ROLES if r not in used_roles] or ADMISSION_ROLES)
            used_roles.append(role)
            db.add(models.AdmissionTeam(
                hospitalization_id=hosp.id,
                staff_id=member.id,
                begin_time=arrival + timedelta(minutes=random.randint(5, 30)),
                end_time=arrival + timedelta(hours=random.randint(1, 8)),
                role=role,
            ))

        # Запись в истории болезни
        doctor = random.choice([s for s in active_staff if s.access_level == 2] or active_staff)
        entry = models.MedEntry(
            patient_id=patient.id,
            staff_id=doctor.id,
            description=(
                f"Диагноз: {diag_name}. "
                f"Жалобы: {fake.sentence(nb_words=8)}. "
                f"Назначено лечение: {treatment_summary}"
            ),
            entry_date=arrival + timedelta(hours=1),
        )
        db.add(entry)
        db.flush()

        # Лист назначений
        for med_name, dose, rules, duration_days in medications:
            db.add(models.MedicationOrder(
                med_entry_id=entry.id,
                name=med_name,
                dose=dose,
                rules_taking=rules,
                begin_date=arrival.date(),
                end_date=(arrival + timedelta(days=duration_days)).date(),
            ))

        # Оплата (70% госпитализаций оплачены)
        if random.random() < 0.7:
            db.add(models.Payment(
                hospitalization_id=hosp.id,
                amount=float(random.randint(3000, 45000)),
                method=random.choice(list(models.PaymentMethod)),
                payment_date=(arrival + timedelta(days=random.randint(0, 3))).date(),
            ))

    db.flush()

    # ── 8. Обратная связь ─────────────────────────
    print("💬 Добавление обратной связи...")
    feedback_authors = random.sample(staff_list, min(len(FEEDBACK_SUBJECTS), len(staff_list)))
    for i, (fb_type, subject, description) in enumerate(FEEDBACK_SUBJECTS):
        db.add(models.Feedback(
            staff_id=feedback_authors[i].id,
            subject=subject,
            description=description,
            feedback_type=models.FeedbackType[fb_type],
            section=random.choice(["patients", "hospitalizations", "staff", "med_entries", None]),
            created_at=datetime.now() - timedelta(days=random.randint(0, 14)),
            is_read=random.random() < 0.5,
        ))

    db.commit()
    print("✅ База данных успешно заполнена!")
    print(f"   Отделений:       {len(DEPARTMENTS)}")
    print(f"   Должностей:      {len(POSITIONS)}")
    print(f"   Помещений:       {len(rooms)}")
    print(f"   Палат:           {len(wards)}")
    print(f"   Сотрудников:     {len(staff_list)}")
    print(f"   Пациентов:       30")
    print(f"   Госпитализаций:  30")
    print(f"   Обращений:       {len(FEEDBACK_SUBJECTS)}")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_all(session)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()
