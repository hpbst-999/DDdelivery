import uuid
from src.identity.domain.exceptions import DomainException, SessionNotFoundError
from src.identity.application.interfaces import IUnitOfWork, ITokenService, TokenPair

class RefreshSessionUseCase:
    def __init__(self, redis_uow: IUnitOfWork, token_service: ITokenService):
        self.redis_uow = redis_uow
        self.token_service = token_service

    def execute(self, raw_refresh_token: str) -> TokenPair:
        try:
            self.token_service.validate_refresh_token(raw_refresh_token)
        except ValueError as e:
            raise DomainException(str(e))
        with self.redis_uow:
            session_data = self.redis_uow.session_repository.get_data_by_token(raw_refresh_token)
            if not session_data:
                raise SessionNotFoundError("Session not found.")

            account_id = session_data["account_id"]
            old_session_id = session_data["session_id"]
            
            new_tokens = self.token_service.generate_pair(account_id=account_id)
            new_session_id = str(uuid.uuid4()) 

            self.redis_uow.session_repository.delete_session(old_session_id)
            self.redis_uow.session_repository.save_refresh_token(
                session_id=new_session_id,
                account_id=account_id,
                refresh_token=new_tokens["refresh_token"],
                expires_days=30
            )
            self.redis_uow.commit()

        return new_tokens