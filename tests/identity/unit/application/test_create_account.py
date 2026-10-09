import uuid
import pytest
from unittest.mock import MagicMock
from datetime import UTC, datetime

from src.identity.application.interfaces import ITokenData, ITokenGenerator
from src.identity.application.use_cases.create_account import CreateAccountUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.exceptions import InvalidCredentialsError
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.phone_number import PhoneNumber
from tests.identity.fakes.fake_uow import FakeUnitOfWork  


@pytest.fixture
def mock_token_data() -> ITokenData:
    token_data = MagicMock(spec=ITokenData)
    token_data.access_token = "access_123"
    token_data.refresh_token = "refresh_123"
    return token_data


@pytest.fixture
def mock_token_generator(mock_token_data: ITokenData) -> MagicMock:
    generator = MagicMock(spec=ITokenGenerator)
    generator.generate_pair.return_value = mock_token_data
    return generator


@pytest.mark.asyncio
async def test_create_account_new_user_by_phone_success(
    mock_token_generator: MagicMock,
    mock_token_data: ITokenData,
) -> None:
    uow = FakeUnitOfWork()
    use_case = CreateAccountUseCase(uow=uow, token_generator=mock_token_generator)
    phone = PhoneNumber("+79991234567")

    result = await use_case.execute(phone_number=phone)

    assert result == mock_token_data
    assert uow.committed is True
    
    assert len(uow.accounts.accounts) == 1
    created_account = list(uow.accounts.accounts.values())[0]
    assert created_account.phone_number == phone

    assert len(uow.user_profiles.profiles) == 1
    created_profile = list(uow.user_profiles.profiles.values())[0]
    assert created_profile.account_id == created_account.id

    assert len(uow.refresh_tokens.tokens) == 1
    saved_token = list(uow.refresh_tokens.tokens.values())[0]
    assert saved_token.account_id == created_account.id
    assert saved_token.refresh_token == mock_token_data.refresh_token


@pytest.mark.asyncio
async def test_create_account_existing_user_by_email_success(
    mock_token_generator: MagicMock,
    mock_token_data: ITokenData,
) -> None:
    uow = FakeUnitOfWork()
    email = Email("user@example.com")
    existing_account = Account(id=uuid.uuid4(), phone_number=None)
    existing_account.email = email
    
    await uow.accounts.add_account(existing_account)

    use_case = CreateAccountUseCase(uow=uow, token_generator=mock_token_generator)

    result = await use_case.execute(email=email)

    assert result == mock_token_data
    assert uow.committed is True
    
    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 0  
    
    assert len(uow.refresh_tokens.tokens) == 1
    saved_token = list(uow.refresh_tokens.tokens.values())[0]
    assert saved_token.account_id == existing_account.id


@pytest.mark.asyncio
async def test_create_account_raises_invalid_credentials_when_args_are_none(
    mock_token_generator: MagicMock,
) -> None:
    uow = FakeUnitOfWork()
    use_case = CreateAccountUseCase(uow=uow, token_generator=mock_token_generator)

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(phone_number=None, email=None)

    assert uow.committed is False
    assert len(uow.accounts.accounts) == 0