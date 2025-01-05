import asyncio
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Consumer


class AIOConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threadpool = ThreadPoolExecutor(max_workers=1)

    async def poll(self, timeout=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._threadpool, super().poll, timeout)

    def close(self):
        self._threadpool.shutdown()
        super().close()

