import signal
import time

from src.core.config import settings
from src.outbox.application.use_cases.process_batch import ProcessOutboxBatchUseCase
from src.outbox.infrastructure.publishers.composite_dispatcher import EventDispatcher
from src.outbox.infrastructure.publishers.sms_service import SmsSenderPublisher
from src.outbox.infrastructure.uow import SQLAlchemyUnitOfWork
from src.core.database import engine, SessionFactory


class OutboxWorker:
    def __init__(self, database_url: str, batch_size: int = 10, poll_interval: float = 10.0,engine =engine, session_factory = SessionFactory ):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._is_running = True
        
        self.engine = engine
        self.session_factory = session_factory

        self.dispatcher = EventDispatcher()
        sms_publisher = SmsSenderPublisher()
        
        self.dispatcher.register("identity.otp_created", sms_publisher.send_sms)

        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum: int, frame: object) -> None:
        print("\n[Outbox Worker] Stopping...")
        self._is_running = False

    def run(self) -> None:
        print(f"[Outbox Worker] Started (batch={self.batch_size}, interval={self.poll_interval}s)")

        while self._is_running:
            with self.session_factory() as session:
                try:
                    uow = SQLAlchemyUnitOfWork(session=session)
                    use_case = ProcessOutboxBatchUseCase(
                        uow=uow,
                        publisher=self.dispatcher,
                        batch_size=self.batch_size,
                    )
                    
                    processed_count = use_case.execute()

                    if processed_count > 0:
                        print(f"[Outbox Worker] Processed {processed_count} message(s)")
                    else:
                        time.sleep(self.poll_interval)

                except Exception as exc:
                    print(f"[Outbox Worker] Error: {exc}")
                    time.sleep(self.poll_interval)

        self.engine.dispose()
        print("[Outbox Worker] Stopped cleanly")


if __name__ == "__main__":
    DATABASE_URL = settings.database_url

    worker = OutboxWorker(database_url=DATABASE_URL)
    worker.run()