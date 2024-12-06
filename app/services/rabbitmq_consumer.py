from os import environ

import aio_pika
from aio_pika import IncomingMessage
from fastapi import HTTPException, status

class RabbitmqConsumer:
    def __init__(self, queue: str):
        self.__host = environ.get('RABBITMQ_HOST')
        self.__port = environ.get('RABBITMQ_PORT')
        self.__username = environ.get('RABBITMQ_DEFAULT_USER')
        self.__password = environ.get('RABBITMQ_DEFAULT_PASS')
        self.__queue = queue
        self.__connection = None
        self.__channel = None

    async def __connect(self):
        try:
            url = f'amqp://{self.__username}:{self.__password}@{self.__host}:{self.__port}/'
            self.__connection = await aio_pika.connect_robust(url)
            self.__channel = await self.__connection.channel()

            await self.__channel.declare_queue(self.__queue, durable=True, arguments={
                "x-overflow": "reject-publish"
            })
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno do servidor."
            )

    async def __callback(message: IncomingMessage):
        async with message.process():
            print(f"Mensagem recebida: {message.body.decode()}")

    async def start(self):
        await self.__connect()
        await self.__channel.consume(self.__callback, queue=self.__queue)
        print(f"RabbitMQ listening on {self.__host}:{self.__port}.")
