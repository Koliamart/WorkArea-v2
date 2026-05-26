"""Публикация события task.created в Kafka (см. AsyncAPI-спецификацию в этом каталоге)."""
from __future__ import annotations

import json
import logging
import os

from kafka import KafkaProducer

logger = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


def _bootstrap_servers() -> list[str]:
    host = os.environ.get('KAFKA_HOST', '127.0.0.1')
    port = os.environ.get('KAFKA_PORT', '9092')
    return [f'{host}:{port}']


def _topic() -> str:
    return os.environ.get('KAFKA_TOPIC_TASK_CREATED', 'task.created')


def _get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=_bootstrap_servers(),
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
        )
    return _producer


def send_task_created_event(task_data: dict) -> None:
    """Отправляет событие создания задачи в топик task.created."""
    producer = _get_producer()
    future = producer.send(_topic(), task_data)
    future.get(timeout=10)
