import asyncio
import json

from confluent_kafka.cimpl import Consumer, TopicPartition

from aio_confluent_kafka import AIOConsumer, AIOProducer
from confluent_kafka.admin import AdminClient, NewTopic

import pytest

@pytest.fixture(autouse=True)
async def setup_topic():
    admin_client = AdminClient({
        'bootstrap.servers': 'localhost:9092',
    })
    admin_client.create_topics([NewTopic("test-topic", num_partitions=1, replication_factor=1)])
    yield
    admin_client.delete_topics(["test-topic"])


async def test_integration():
    producer = AIOProducer({
        'bootstrap.servers': 'localhost:9092',
    })

    message = {"message": "hello"}
    raw_message = json.dumps(message).encode("utf-8")
    message_event = asyncio.Event()

    async def message_callback(error, msg):
        print("Received message")
        message_event.set()

    await producer.produce(topic='test-topic', value=raw_message, partition=0, on_delivery=message_callback)
    producer.flush()
    await asyncio.wait_for(message_event.wait(), timeout=2)

    consumer = AIOConsumer({
        "group.id": "abc",
        'bootstrap.servers': 'localhost:9092',
        'session.timeout.ms': 6000,
        "enable.auto.commit": True,
        "auto.offset.reset": "earliest"
    })

    wait_assigned = asyncio.Event()
    loop = asyncio.get_event_loop()

    def _on_assign(abc: Consumer, partitions: list[TopicPartition]) -> None:
        print(f"Assigned partitions={partitions} to consumer={abc}")

        async def set_event():
            wait_assigned.set()

        asyncio.run_coroutine_threadsafe(set_event(), loop)

    consumer.subscribe(topics=['test-topic'], on_assign=_on_assign)
    raw_message = await consumer.poll(timeout=5)
    assert raw_message is not None

    await asyncio.wait_for(wait_assigned.wait(), timeout=5)
    assert json.loads(raw_message.value()) == message
