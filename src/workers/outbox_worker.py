import signal
import asyncio

from src.core.config import settings
from src.outbox.application.use_cases.process_batch import ProcessOutboxBatchUseCase
from src.outbox.infrastructure.publishers.composite_dispatcher import EventDispatcher
from src.outbox.infrastructure.publishers.sms_service import SmsSenderPublisher
from src.outbox.infrastructure.uow import SQLAlchemyUnitOfWork
from src.core.database import engine, SessionFactory


class OutboxWorker:
    def __init__(self, batch_size: int = 10, poll_interval: float = 10.0,engine =engine, session_factory = SessionFactory):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._is_running = True
        
        self.engine = engine
        self.session_factory = session_factory

        self.dispatcher = EventDispatcher()
        sms_publisher = SmsSenderPublisher()
        
        self.dispatcher.register("identity.otp_created", sms_publisher.send_sms)

        

    def _setup_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()

        def _shutdown():
            print("\n[Outbox Worker] Stopping...")
            self._is_running = False

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _shutdown)
            except NotImplementedError:
                signal.signal(sig, lambda s, f: _shutdown())

    async def run(self) -> None:
        self._setup_signal_handlers()
        print(f"[Outbox Worker] Started (batch={self.batch_size}, interval={self.poll_interval}s)")

        while self._is_running:
            async with self.session_factory() as session:
                try:
                    async with SQLAlchemyUnitOfWork(session=session) as uow:
                        use_case = ProcessOutboxBatchUseCase(
                            uow=uow,
                            publisher=self.dispatcher,
                            batch_size=self.batch_size,
                        )
                    
                    processed_count = await use_case.execute()

                    if processed_count > 0:
                        print(f"[Outbox Worker] Processed {processed_count} message(s)")
                        await asyncio.sleep(2.0)
                    else:
                        await asyncio.sleep(self.poll_interval)

                except Exception as exc:
                    print(f"[Outbox Worker] Error: {exc}")
                    await asyncio.sleep(self.poll_interval)

        await self.engine.dispose()
        print("[Outbox Worker] Stopped cleanly")


if __name__ == "__main__":

    worker = OutboxWorker()
    asyncio.run(worker.run())