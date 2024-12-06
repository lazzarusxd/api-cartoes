from os import environ
import json
from typing import Dict

import aio_pika
from fastapi import HTTPException, status


class RabbitmqPublisher:
    def __init__(self, exchange: str, routing_key: str):
        self.__host = environ.get('RABBITMQ_HOST')
        self.__port = environ.get('RABBITMQ_PORT')
        self.__username = environ.get('RABBITMQ_DEFAULT_USER')
        self.__password = environ.get('RABBITMQ_DEFAULT_PASS')
        self.__exchange = exchange
        self.__routing_key = routing_key
        self.__connection = None
        self.__channel = None

    async def __connect(self):
        try:
            url = f'amqp://{self.__username}:{self.__password}@{self.__host}:{self.__port}/'
            self.__connection = await aio_pika.connect_robust(url)
            self.__channel = await self.__connection.channel()

            await self.__channel.declare_exchange(self.__exchange, aio_pika.ExchangeType.DIRECT, durable=True)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno do servidor."
            )

    async def send_message(self, body: Dict):
        await self.__connect()

        try:
            message_body = aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.__channel.default_exchange.publish(
                message_body,
                routing_key=self.__routing_key
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno do servidor."
            )
