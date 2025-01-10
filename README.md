# `aio_confluent_kafka`

A lightweight wrapper around `confluent_kafka` to enable use with asyncio 

`pip install aio_confluent_kafka`

# Consumer

```python



from aio_confluent_kafka import AIOConsumer

async def run_consumer():
    consumer = AIOConsumer({
            "group.id": "abc",
            'bootstrap.servers': 'localhost:9092',
            'session.timeout.ms': 6000,
            "enable.auto.commit": True,
            "auto.offset.reset": "earliest"
    })
    consumer.subscribe(["test-topic"])
    raw_message = await consumer.poll(timeout=5)
```

# Producer 

```python
from aio_confluent_kafka import AIOProducer
import asyncio

async def produce(bytes_message: bytes):
    producer = AIOProducer({
        'bootstrap.servers': 'localhost:9092',
    })

    message_event = asyncio.Event()
    
    # Supports async callbacks
    async def message_callback(error, msg):
        message_event.set()

    await producer.produce(topic='test-topic', value=bytes_message, partition=0, on_delivery=message_callback)
    producer.flush()
    await asyncio.wait_for(message_event.wait(), timeout=2)
```
