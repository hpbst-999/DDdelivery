import uuid
import pytest

from src.identity.domain.entities.account import Account
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.value_objects.email import Email


def test_account_creation_with_value_objects():
    acc_id = uuid.uuid4()
    phone = PhoneNumber("+79991234567")
    email = Email("test@example.com")
    
    account = Account(id=acc_id, phone_number=phone, email=email)
    
    assert account.id == acc_id
    assert account.phone_number == phone
    assert account.email == email


def test_account_to_dict_serialization():
    acc_id = uuid.uuid4()
    account = Account(
        id=acc_id, 
        phone_number=PhoneNumber("+79991234567"), 
        email=Email("test@example.com")
    )
    
    data = account.to_dict()
    assert data["id"] == str(acc_id)
    assert data["phone_number"] == "+79991234567"
    assert data["email"] == "test@example.com"


def test_account_from_dict_deserialization():
    acc_id = str(uuid.uuid4())
    data = {
        "id": acc_id,
        "phone_number": "+79991234567",
        "email": "test@example.com"
    }
    
    account = Account.from_dict(data)
    
    assert isinstance(account.id, uuid.UUID)
    assert str(account.id) == acc_id
    
    assert isinstance(account.phone_number, PhoneNumber)
    assert account.phone_number == "+79991234567"
    
    assert isinstance(account.email, Email)
    assert account.email == "test@example.com"


def test_account_to_dict_and_from_dict_with_none_values():
    acc_id = uuid.uuid4()
    account = Account(id=acc_id, phone_number=None, email=None)
    
    data = account.to_dict()
    
    assert data["phone_number"] is None
    assert data["email"] is None
    
    restored_account = Account.from_dict(data)
    
    assert restored_account.phone_number is None
    assert restored_account.email is None
    assert restored_account.id == acc_id