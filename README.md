# Hospital Inpatient Management System (HIMS) 🏥

Информационная система для управления стационаром больницы. Проект включает в себя полноценный REST API на Python и графический интерфейс для управления данными пациентов, персонала и госпитализаций.

## 🚀 Основные возможности
* **Учет пациентов:** регистрация, история госпитализаций и медицинские записи.
* **Управление персоналом:** иерархия должностей, роли и закрепление за палатами.
* **Финансовый блок:** учет платежей и методов оплаты.
* **Системное администрирование:** автоматическое создание дампов (бэкапов) базы данных PostgreSQL через API.
* **Тестирование:** полное покрытие тестами (pytest) основных роутеров системы.

## 🛠 Стек технологий
* **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pydantic.
* **Frontend:** PySide6 (Qt for Python).
* **Environment:** Python 3.12, `uvicorn`, `python-dotenv`.

## 📦 Установка и запуск

### 1. Подготовка окружения
Склонируйте репозиторий и создайте виртуальное окружение:
```bash
git clone [https://github.com/I-Need-Help-Pls-T-T/Hospital-Inpatient-Management-System.git](https://github.com/I-Need-Help-Pls-T-T/Hospital-Inpatient-Management-System.git)
cd Hospital-Inpatient-Management-System
python -m venv venv
source venv/Scripts/activate  # Для Windows

```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt

```

### 3. Настройка базы данных

Создайте файл `.env` в корне проекта по шаблону:

```env
DB_NAME=hospital_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
BACKUP_DIR=backups

```

### 4. Запуск приложения

1. **Запуск сервера API:**
```bash
uvicorn backend.main:app --reload

```


2. **Запуск GUI-интерфейса:**
```bash
python main.py

```



## 🧪 Тестирование

Для запуска тестов используйте команду:

```bash
pytest test-server/

```

## 📂 Структура проекта

* `backend/` — логика сервера, модели БД и API эндпоинты.
* `frontend/` — интерфейс пользователя (UI файлы и контроллеры).
* `backups/` — директория для хранения снимков базы данных.
* `test-server/` — набор интеграционных и юнит-тестов.
