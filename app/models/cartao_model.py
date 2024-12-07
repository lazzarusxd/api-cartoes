import uuid
import enum
import random
from calendar import monthrange
from datetime import datetime, timedelta, date, timezone

from sqlalchemy import Enum, Column, Integer, String, Date, select, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from jose import jwt

from app.database.base import Base, get_session
from app.core.configs import settings
from app.core.auth import criar_token_acesso


class StatusEnum(enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    CANCELADO = "CANCELADO"
    BLOQUEADO = "BLOQUEADO"
    ENVIADO = "ENVIADO"
    EXPIRADO = "EXPIRADO"
    EM_ANALISE = "EM_ANALISE"
    BLACKLISTED = "BLACKLISTED"


class CartaoModel(Base):
    __tablename__ = 'cartoes'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    titular_cartao = Column(String, index=True, nullable=False)
    cpf_titular = Column(String, index=True, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.EM_ANALISE)
    email = Column(String, nullable=False)
    endereco = Column(String, index=True, nullable=False)
    saldo = Column(Float, nullable=False, default=0)
    numero_cartao = Column(String, nullable=False, unique=True)
    expiracao = Column(Date, nullable=False)
    cvv = Column(String, nullable=False)
    data_criacao = Column(DateTime(timezone=True), nullable=False)
    token = Column(String, nullable=False)
    token_expiracao = Column(DateTime(timezone=True), nullable=False)

    def __init__(self, titular_cartao, cpf_titular, endereco, email):
        super().__init__()
        self.titular_cartao = titular_cartao
        self.cpf_titular = cpf_titular
        self.endereco = endereco
        self.email = email

    async def initialize(self):
        self.numero_cartao = await self.set_hash_cartao()
        self.cvv = self.set_hash_cvv()
        self.expiracao = self.gerar_data_expiracao()
        self.data_criacao = self.gerar_data_criacao()
        self.token, self.token_expiracao = await self.gerar_ou_atualizar_token()

    async def set_hash_cartao(self) -> str:
        numero_cartao = await self._gerar_numero_cartao()
        return self.gerar_hash_cartao(numero_cartao)

    @staticmethod
    async def _gerar_numero_cartao() -> str:
        while True:
            numero_cartao = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            if CartaoModel.validar_cartao(numero_cartao):
                if not await CartaoModel.verificar_hash_cartao_unico(numero_cartao):
                    return numero_cartao

    @staticmethod
    def validar_cartao(numero_cartao: str) -> bool:
        soma = 0
        invertido = numero_cartao[::-1]

        for i, digito in enumerate(invertido):
            n = int(digito)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            soma += n

        return soma % 10 == 0

    @staticmethod
    async def verificar_hash_cartao_unico(numero_cartao: str) -> bool:
        hash_cartao = CartaoModel.gerar_hash_cartao(numero_cartao)
        async for session in get_session():
            query = await session.execute(
                select(CartaoModel).filter_by(numero_cartao=hash_cartao)
            )
            if query is not None:
                exists = query.scalars().first()
                return exists is not None
        return False

    @staticmethod
    def gerar_hash_cartao(numero_cartao: str) -> str:
        payload = {"numero_cartao": numero_cartao}
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM
        )
        return token

    def set_hash_cvv(self) -> str:
        cvv = self.gerar_cvv()
        return self.gerar_hash_cvv(cvv)

    @staticmethod
    def gerar_cvv() -> str:
        return ''.join([str(random.randint(0, 9)) for _ in range(3)])

    @staticmethod
    def gerar_hash_cvv(cvv: str) -> str:
        payload = {"cvv": cvv}
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM
        )
        return token

    @staticmethod
    def gerar_data_expiracao() -> date:
        data_expiracao = datetime.now(timezone.utc) + timedelta(days=5 * 365)
        ultimo_dia_do_mes = monthrange(data_expiracao.year, data_expiracao.month)[1]
        return datetime(data_expiracao.year, data_expiracao.month, ultimo_dia_do_mes).date()

    @staticmethod
    def gerar_data_criacao() -> datetime:
        return datetime.now(timezone.utc)

    async def gerar_ou_atualizar_token(self):
        async for db in get_session():
            query = await db.execute(
                select(CartaoModel).where(
                    CartaoModel.cpf_titular == self.cpf_titular
                )
            )
            cartoes = query.scalars().all()

            if cartoes:
                token_existente = next(
                    (
                        cartao
                        for cartao in cartoes
                        if cartao.token_expiracao > datetime.now(timezone.utc)
                    ),
                    None
                )
                if token_existente:
                    return token_existente.token, token_existente.token_expiracao
                else:
                    novo_token = self.gerar_hash_token(self.cpf_titular)
                    nova_expiracao = datetime.now(timezone.utc) + timedelta(weeks=1)

                    for cartao in cartoes:
                        cartao.token = novo_token
                        cartao.token_expiracao = nova_expiracao

                    await db.commit()

                    return novo_token, nova_expiracao
            else:
                novo_token = self.gerar_hash_token(self.cpf_titular)
                token_expiracao = datetime.now(timezone.utc) + timedelta(weeks=1)

                return novo_token, token_expiracao

    @staticmethod
    def gerar_hash_token(cpf_titular: str) -> str:
        token = criar_token_acesso(cpf_titular)
        payload = {"token": token}
        hash_token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM,
        )
        return hash_token

    @staticmethod
    def _descriptografar_hash_cartao(numero_cartao: str) -> str:
        payload = jwt.decode(
            numero_cartao,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("numero_cartao")

    @staticmethod
    def _descriptografar_hash_cvv(hash_cvv: str) -> str:
        payload = jwt.decode(
            hash_cvv,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("cvv")

    @staticmethod
    def _descriptografar_hash_token(hash_token: str):
        payload = jwt.decode(
            hash_token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("token")

    @property
    def numero_cartao_descriptografado(self) -> str:
        return self._descriptografar_hash_cartao(self.numero_cartao)

    @property
    def cvv_descriptografado(self) -> str:
        return self._descriptografar_hash_cvv(self.cvv)

    @property
    def hash_token_descriptografado(self) -> str:
        return self._descriptografar_hash_token(self.token)
