from src.identity.application.interfaces import IUnitOfWork

class LogoutUseCase:
    def __init__(self, redis_uow: IUnitOfWork):
        self.redis_uow = redis_uow 

    def execute(self, raw_refresh_token: str) -> None:
        with self.redis_uow:
            session_data = self.redis_uow.session_repository.get_data_by_token(raw_refresh_token)
            if not session_data:
                return

            session_id = session_data["session_id"]
            self.redis_uow.session_repository.delete_session(session_id)
            
            self.redis_uow.commit()