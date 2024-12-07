import json
from os import environ
from uuid import UUID
from email.message import EmailMessage

import aiosmtplib
import aio_pika
from fastapi import HTTPException, status


class RabbitmqConsumer:
    def __init__(self, queue: str):
        self.__host = environ.get('RABBITMQ_HOST')
        self.__port = int(environ.get('RABBITMQ_PORT'))
        self.__username = environ.get('RABBITMQ_DEFAULT_USER')
        self.__password = environ.get('RABBITMQ_DEFAULT_PASS')
        self.__queue = queue
        self.__connection = None
        self.__channel = None

    async def __connect(self):
        try:
            url = f"amqp://{self.__username}:{self.__password}@{self.__host}:{self.__port}/"
            self.__connection = await aio_pika.connect_robust(url)
            self.__channel = await self.__connection.channel()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor."
            )

    async def consume_messages(self, uuid: UUID):
        if not self.__connection or self.__connection.is_closed:
            await self.__connect()

        queue = await self.__channel.declare_queue(
            self.__queue,
            durable=True,
            arguments={
                "x-overflow": "reject-publish"
            }
        )

        async for message in queue:
            message_body = message.body.decode()

            data = json.loads(message_body)
            uuid_msg = UUID(data["data"]["uuid"])

            if uuid_msg == uuid:
                titular_cartao = data["data"]["titular_cartao"]
                email = data["data"]["email"]

                await self.__send_email(uuid_msg, titular_cartao, email)

                await message.ack()

                await self.__close_connection()

                break

    @staticmethod
    async def __send_email(uuid: UUID, titular_cartao: str, email: str):
        smtp_user = environ.get("SMTP_USER")
        smtp_password = environ.get("SMTP_PASSWORD")
        smtp_host = environ.get("SMTP_HOST", "smtp.mailgun.org")
        smtp_port = int(environ.get("SMTP_PORT"))

        message = EmailMessage()
        message["From"] = smtp_user
        message["To"] = email
        message["Subject"] = "Confirmação de Ativação do Cartão"
        message.set_content(
            f"Olá {titular_cartao},\n\n"
            f"Seu cartão com o UUID ({uuid}) foi ativado com sucesso!\n\n"
            "Obrigado por utilizar nossos serviços.\n\n"
            "Atenciosamente,\nEquipe de Suporte"
        )

        max_retries = 3
        attempt = 1

        while attempt <= max_retries:
            try:
                print(f"Tentando enviar o e-mail... Tentativa {attempt}/{max_retries}")

                async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10) as client:
                    await client.login(smtp_user, smtp_password)
                    await client.send_message(message)

                    print("E-mail enviado com sucesso!")
                    break

            except aiosmtplib.SMTPException as e:
                print(f"Falha ao enviar e-mail (Tentativa {attempt}/{max_retries}): {e}")
            except Exception as e:
                print(f"Ocorreu um erro inesperado (Tentativa {attempt}/{max_retries}): {e}")

            attempt += 1

        if attempt > max_retries:
            print("Máximo de tentativas alcançado. O envio do e-mail falhou.")

    async def __close_connection(self):
        if self.__connection:
            await self.__connection.close()
            print("Conexão com RabbitMQ encerrada.")
