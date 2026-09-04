from typing import Any, Callable, Awaitable
import uuid

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]

class EventDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, EventHandler] = {}

    def register(self, type: str, handler: EventHandler) -> None:
        self._handlers[type] = handler

    async def publish(self, type: str, payload: dict[str, Any]) -> None:
        handler = self._handlers.get(type)
        if not handler:
            raise ValueError(f"No handler registered for event type: '{type}'")
        
        await handler(payload)