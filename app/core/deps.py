from uuid import UUID

from fastapi import Depends, HTTPException, status, Path
from jose import jwt, JWTError
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.auth import oauth2_schema
from app.models.cartao_model import CartaoModel
from app.core.configs import settings
from app.database.base import get_session
from app.schemas.cartao_schema import CartaoTransferir, CartaoRecarga

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credencial inválida para o CPF vinculado.",
    headers={
        "WWW-Authenticate": "Bearer",
        "Authorization": "Bearer token_value",
        "Content-Type": "application/json"
    }
)


async def auth_cartoes_por_cpf(
        cpf_titular: str = Path(
            title="CPF do titular",
            description="CPF do titular do cartão."
        ),
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_session)
) -> str:
    try:
        query1 = await db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.cpf_titular == cpf_titular
                )
            )
        )
        cartao = query1.scalars().first()

        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CPF informado não está vinculado a nenhum cartão ou é inválido."
            )

        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        token_cpf = payload.get("sub")

        if not token_cpf or token_cpf != cpf_titular:
            raise credential_exception

        query2 = await db.execute(
            select(CartaoModel).where(
                CartaoModel.cpf_titular == token_cpf
            )
        )
        cartao = query2.scalars().first()

        if not cartao or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return token_cpf

    except JWTError:
        raise credential_exception


async def auth_atualizar_informacoes(
        uuid: UUID = Path(
            title="UUID do cartão",
            description="UUID do cartão a ser atualizado."
        ),
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_session)
) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        token_cpf = payload.get("sub")

        if not token_cpf:
            raise credential_exception

        query = await db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.uuid == uuid)
            )
        )
        cartao = query.scalars().first()

        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado, verifique o UUID."
            )

        if cartao.cpf_titular != token_cpf or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return cartao.uuid

    except JWTError:
        raise credential_exception


async def auth_recarregar_cartao(
        recarga: CartaoRecarga,
        uuid: UUID = Path(
            title="UUID do cartão",
            description="UUID do cartão do titular."
        ),
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_session)
) -> CartaoRecarga:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        token_cpf = payload.get("sub")

        if not token_cpf:
            raise credential_exception

        query = await db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.uuid == uuid
                )
            )
        )
        cartao = query.scalars().first()

        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado, verifique o UUID."
            )

        if token_cpf != cartao.cpf_titular or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return CartaoRecarga(valor=recarga.valor)

    except JWTError:
        raise credential_exception


async def auth_transferir_saldo(
        transferencia: CartaoTransferir,
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_session)
) -> CartaoTransferir:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        token_cpf = payload.get("sub")

        query = await db.execute(
            select(CartaoModel).where(
                and_(CartaoModel.uuid == transferencia.uuid_pagante)
            )
        )
        cartao = query.scalars().first()

        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado, verifique o UUID do pagante."
            )

        if token_cpf != cartao.cpf_titular or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return CartaoTransferir(
            uuid_pagante=transferencia.uuid_pagante,
            uuid_recebente=transferencia.uuid_recebente,
            valor=transferencia.valor)

    except JWTError:
        raise credential_exception
