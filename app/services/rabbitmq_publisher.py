from os import environ
import json
from typing import Dict

import aio_pika
from fastapi import HTTPException, status


class RabbitmqPublisher:
    def __init__(self, exchange: str, routing_key: str):
        self.__host = environ.get('RABBITMQ_HOST')
        self.__port = int(environ.get('RABBITMQ_PORT'))
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

            await self.__channel.declare_exchange(
                self.__exchange,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor ao conectar ao RabbitMQ."
            )

    async def send_message(self, body: Dict):
        await self.__connect()

        try:
            exchange = await self.__channel.get_exchange(self.__exchange)

            message_body = aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(
                message_body,
                routing_key=self.__routing_key
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor ao enviar mensagem para RabbitMQ."
            )
        finally:
            if self.__connection:
                await self.__connection.close()
