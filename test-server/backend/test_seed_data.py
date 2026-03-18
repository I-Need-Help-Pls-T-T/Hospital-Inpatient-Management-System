import pytest
from unittest.mock import MagicMock, patch, ANY
from backend.seed_data import seed_all
from backend import models

@pytest.fixture
def mock_db():
    """
    Улучшенная фикстура для имитации сессии БД.
    Настраиваем mock так, чтобы при обращении к .id у созданных объектов
    не возникало ошибок и возвращалось случайное число.
    """
    db = MagicMock()

    # Имитируем успешное удаление (db.query(Model).delete())
    db.query.return_value.delete.return_value = None

    # Настраиваем поведение для db.add:
    # Присваиваем фиктивный ID объекту, чтобы последующий код seed_all мог его прочитать
    def side_effect_add(obj):
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = 1  # Упрощенно даем всем ID = 1 для тестов
        return None

    db.add.side_effect = side_effect_add
    return db

def test_seed_all_cleanup_called(mock_db):
    """Проверка, что очистка вызвана для всех таблиц в правильном порядке"""
    seed_all(mock_db)

    # Список моделей, которые должны быть очищены
    expected_models = [
        models.Payment, models.MedicationOrder, models.MedEntry,
        models.AdmissionTeam, models.PatientAdmission, models.Hospitalization,
        models.StaffRole, models.Staff, models.Patient, models.Ward,
        models.Room, models.Position, models.Department
    ]

    # Проверяем, что для каждой модели был вызван query()
    called_models = [call.args[0] for call in mock_db.query.call_args_list]
    for model in expected_models:
        assert model in called_models, f"Модель {model} не была очищена"

def test_seed_all_creates_entities(mock_db):
    """Проверка создания ключевых сущностей (Department, Staff, Patient и т.д.)"""
    seed_all(mock_db)

    # Проверяем, что db.add вызывался многократно
    # (В seed_all создается около 50+ объектов)
    assert mock_db.add.call_count >= 50

def test_seed_all_flush_and_commit(mock_db):
    """Проверка вызовов flush и commit для сохранения связей"""
    seed_all(mock_db)

    # flush() нужен для получения ID между этапами создания
    assert mock_db.flush.called
    # commit() завершает транзакцию
    assert mock_db.commit.called

@patch('backend.seed_data.fake')
def test_seed_all_integrity(mock_fake, mock_db):
    """Проверка, что данные генерируются без ошибок типов"""
    mock_fake.name.return_value = "Тестовое Имя"
    mock_fake.phone_number.return_value = "123456789"

    # Если в seed_all есть ошибка в именах полей (как была с lvl_responsibility),
    # этот вызов упадет с TypeError
    try:
        seed_all(mock_db)
    except TypeError as e:
        pytest.fail(f"Ошибка в именах полей моделей: {e}")
    except Exception as e:
        pytest.fail(f"Сидинг упал с ошибкой: {e}")

def test_seed_all_order_of_deletion(mock_db):
    """
    Проверка порядка удаления.
    Важно, чтобы дочерние таблицы (Payment) удалялись РАНЬШЕ родительских (Department).
    """
    seed_all(mock_db)

    calls = [call.args[0] for call in mock_db.query.call_args_list]

    idx_payment = calls.index(models.Payment)
    idx_dept = calls.index(models.Department)

    assert idx_payment < idx_dept, "Payment должен удаляться раньше Department из-за FK"
