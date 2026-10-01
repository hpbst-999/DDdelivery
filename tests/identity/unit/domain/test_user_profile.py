import uuid

import pytest

from src.identity.domain.entities.user_profile import UserProfile


@pytest.fixture
def profile_data():
    return {
        "id": uuid.uuid4(),
        "account_id": uuid.uuid4(),
        "name": "Иван Иванов",
        "address": "г. Москва, ул. Пушкина, д. 1",
    }


def test_user_profile_creation(profile_data):
    profile = UserProfile(
        id=profile_data["id"],
        account_id=profile_data["account_id"],
        name=profile_data["name"],
        address=profile_data["address"],
    )

    assert profile.id == profile_data["id"]
    assert profile.account_id == profile_data["account_id"]
    assert profile.name == profile_data["name"]
    assert profile.address == profile_data["address"]


def test_user_profile_creation_with_none_values():
    profile_id = uuid.uuid4()
    account_id = uuid.uuid4()

    profile = UserProfile(id=profile_id, account_id=account_id)

    assert profile.id == profile_id
    assert profile.account_id == account_id
    assert profile.name is None
    assert profile.address is None


def test_user_profile_to_dict(profile_data):
    profile = UserProfile(**profile_data)

    data = profile.to_dict()

    assert data["id"] == str(profile_data["id"])
    assert data["account_id"] == str(profile_data["account_id"])
    assert data["name"] == profile_data["name"]
    assert data["address"] == profile_data["address"]


def test_user_profile_from_dict():
    profile_id_str = str(uuid.uuid4())
    account_id_str = str(uuid.uuid4())

    data = {
        "id": profile_id_str,
        "account_id": account_id_str,
        "name": "Петр Петров",
        "address": "г. Казань",
    }

    profile = UserProfile.from_dict(data)

    assert isinstance(profile.id, uuid.UUID)
    assert str(profile.id) == profile_id_str

    assert isinstance(profile.account_id, uuid.UUID)
    assert str(profile.account_id) == account_id_str

    assert profile.name == "Петр Петров"
    assert profile.address == "г. Казань"


def test_user_profile_from_dict_missing_optional_keys():
    profile_id_str = str(uuid.uuid4())
    account_id_str = str(uuid.uuid4())

    data = {
        "id": profile_id_str,
        "account_id": account_id_str,
    }

    profile = UserProfile.from_dict(data)

    assert str(profile.id) == profile_id_str
    assert str(profile.account_id) == account_id_str
    assert profile.name is None
    assert profile.address is None
