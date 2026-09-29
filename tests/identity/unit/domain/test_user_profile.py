import uuid
import pytest

from src.identity.domain.entities.user_profile import UserProfile  # Замени на свой путь импорта


@pytest.fixture
def profile_data():
    """Фикстура с тестовыми данными для профиля."""
    return {
        "id": uuid.uuid4(),
        "account_id": uuid.uuid4(),
        "name": "Иван Иванов",
        "address": "г. Москва, ул. Пушкина, д. 1"
    }


def test_user_profile_creation(profile_data):
    """Тест: Профиль успешно создается со всеми переданными данными."""
    profile = UserProfile(
        id=profile_data["id"],
        account_id=profile_data["account_id"],
        name=profile_data["name"],
        address=profile_data["address"]
    )

    assert profile.id == profile_data["id"]
    assert profile.account_id == profile_data["account_id"]
    assert profile.name == profile_data["name"]
    assert profile.address == profile_data["address"]


def test_user_profile_creation_with_none_values():
    """Тест: Профиль успешно создается, если опциональные поля (name, address) равны None."""
    profile_id = uuid.uuid4()
    account_id = uuid.uuid4()
    
    profile = UserProfile(id=profile_id, account_id=account_id)

    assert profile.id == profile_id
    assert profile.account_id == account_id
    assert profile.name is None
    assert profile.address is None


def test_user_profile_to_dict(profile_data):
    """Тест: Метод to_dict правильно преобразует UUID в строки."""
    profile = UserProfile(**profile_data)
    
    data = profile.to_dict()

    assert data["id"] == str(profile_data["id"])
    assert data["account_id"] == str(profile_data["account_id"])
    assert data["name"] == profile_data["name"]
    assert data["address"] == profile_data["address"]


def test_user_profile_from_dict():
    """Тест: Метод from_dict правильно собирает объект, конвертируя строки обратно в UUID."""
    profile_id_str = str(uuid.uuid4())
    account_id_str = str(uuid.uuid4())
    
    data = {
        "id": profile_id_str,
        "account_id": account_id_str,
        "name": "Петр Петров",
        "address": "г. Казань"
    }

    profile = UserProfile.from_dict(data)

    assert isinstance(profile.id, uuid.UUID)
    assert str(profile.id) == profile_id_str
    
    assert isinstance(profile.account_id, uuid.UUID)
    assert str(profile.account_id) == account_id_str
    
    assert profile.name == "Петр Петров"
    assert profile.address == "г. Казань"


def test_user_profile_from_dict_missing_optional_keys():
    """Тест: Метод from_dict не падает, если в словаре нет ключей name и address."""
    profile_id_str = str(uuid.uuid4())
    account_id_str = str(uuid.uuid4())
    
    # Имитируем словарь, в котором вообще нет ключей name и address (например, пришел неполный JSON)
    data = {
        "id": profile_id_str,
        "account_id": account_id_str,
    }

    profile = UserProfile.from_dict(data)

    assert str(profile.id) == profile_id_str
    assert str(profile.account_id) == account_id_str
    # Благодаря использованию data.get() в классе, эти поля безопасно станут None
    assert profile.name is None
    assert profile.address is None