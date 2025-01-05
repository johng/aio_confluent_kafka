import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Awaitable, Any

from confluent_kafka import Producer, KafkaError, Message

AsyncCallback = Callable[[KafkaError | None, Message], Awaitable[None]]


class AIOProducer(Producer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def produce(
        self,
        topic: str,
        key: Any | None = None,
        value: Any | None = None,
        partition: int = -1,
        on_delivery: AsyncCallback | None = None,
        timestamp: int = 0,
        headers: dict | None = None,
    ) -> None:
        loop = asyncio.get_event_loop()
        if on_delivery is not None:
            def _wraps_async(error: KafkaError | None, message: Message) -> None:
                asyncio.run_coroutine_threadsafe(on_delivery(error, message), loop)
        else:
            _wraps_async = None
        super().produce(topic, key=key, value=value, partition=partition, on_delivery=_wraps_async, headers=headers, timestamp=timestamp)
