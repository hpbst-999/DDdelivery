from src.outbox.application.interfaces import IOutboxUnitOfWork, IMessagePublisher

class ProcessOutboxBatchUseCase:
    def __init__(self, uow: IOutboxUnitOfWork, publisher: IMessagePublisher, batch_size: int = 10):
        self.uow = uow
        self.publisher = publisher
        self.batch_size = batch_size

    async def execute(self) -> int:
        async with self.uow:
            messages = await self.uow.outbox.get_pending_batch(limit=self.batch_size)
            if not messages:
                return 0

            for message in messages:
                try:
                    await self.publisher.publish(
                        type=message.type,
                        payload=message.payload,
                    )
                    message.event_as_processed()
                except Exception as e:
                    print(str(e))
                    message.event_failed()
                await self.uow.outbox.update(message)
                
        return len(messages)