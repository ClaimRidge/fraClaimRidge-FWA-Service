from confluent_kafka import Consumer, KafkaException
import json
import asyncio
from src.config import settings
from src.kafka.handlers import ClaimEventHandler
from structlog import get_logger

logger = get_logger()

class FraudKafkaConsumer:
    def __init__(self, handler: ClaimEventHandler):
        self.handler = handler
        self.consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest'
        })

    async def start(self):
        """
        Subscribes to tenant-prefixed claim topics and processes events.
        """
        # In a real app, we might query a list of active tenants
        # For now, we subscribe to a wildcard or specific pattern
        self.consumer.subscribe([f"^.*\\.claims\\.submitted$"])

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue

                if msg.error():
                    logger.error("kafka_error", error=str(msg.error()))
                    continue

                try:
                    event_data = json.loads(msg.value().decode('utf-8'))
                    # Extract tenant_id from topic name or payload
                    topic = msg.topic()
                    tenant_id = topic.split('.')[0]
                    
                    # Process event
                    await self.handler.handle_claim_submitted(tenant_id, event_data)
                    
                except Exception as e:
                    logger.exception("event_processing_failed", error=str(e))

        finally:
            self.consumer.close()
