from uuid import UUID

from fastapi import status, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cartao_model import CartaoModel, StatusEnum
from app.database.base import get_session
from app.schemas.cartao_schema import (CartaoRequest, CartaoResponse, CartaoRequestResponse, CartaoUpdate,
                                       CartoesPorCpfResponse, CartaoTransferir, CartaoRecarga)


class CartaoServices:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def solicitar_cartao(self, dados_cartao: CartaoRequest) -> dict:
        query = await self.db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.cpf_titular == dados_cartao.cpf_titular
                )
            )
        )
        usuario_existente = query.scalars().all()

        for usuario in usuario_existente:
            if usuario.titular_cartao.upper() != dados_cartao.titular_cartao.upper():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já cadastrado para um titular diferente."
                )

        cartao = CartaoModel(
            titular_cartao=dados_cartao.titular_cartao.upper(),
            cpf_titular=dados_cartao.cpf_titular,
            endereco=dados_cartao.endereco.upper()
        )

        await cartao.initialize()

        try:
            self.db.add(cartao)
            await self.db.commit()
            await self.db.refresh(cartao)
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar cartão. Tente novamente mais tarde."
            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "message": "Cartão criado com sucesso.",
            "data": CartaoRequestResponse.from_model(cartao)
        }

    async def cartoes_por_cpf(self, cpf_titular: str) -> dict:
        query = await self.db.execute(
            select(CartaoModel).where(
                and_(CartaoModel.cpf_titular == cpf_titular)
            )
        )
        cartoes = query.scalars().all()

        if not cartoes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="O CPF informado não foi encontrado."
            )

        cartoes_response = [CartaoResponse.from_model(cartao) for cartao in cartoes]

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Todos os cartões foram listados com sucesso.",
            "data": CartoesPorCpfResponse(cartoes=cartoes_response),
        }

    async def atualizar_info(self, dados_atualizados: CartaoUpdate, uuid: UUID) -> dict:
        if not dados_atualizados.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhum campo para atualizar foi fornecido."
            )

        query1 = await self.db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.uuid == uuid
                )
            )
        )
        cartao = query1.scalars().first()

        if dados_atualizados.titular_cartao is not None or dados_atualizados.endereco is not None:
            query2 = await self.db.execute(
                select(CartaoModel).where(
                    and_(
                        CartaoModel.cpf_titular == cartao.cpf_titular,
                        CartaoModel.titular_cartao == cartao.titular_cartao
                    )
                )
            )
            cartoes_para_atualizar = query2.scalars().all()

            if dados_atualizados.titular_cartao is not None:
                for cartao_atualizar in cartoes_para_atualizar:
                    cartao_atualizar.titular_cartao = dados_atualizados.titular_cartao

            if dados_atualizados.endereco is not None:
                for cartao_atualizar in cartoes_para_atualizar:
                    cartao_atualizar.endereco = dados_atualizados.endereco

        if dados_atualizados.status is not None:
            cartao.status = dados_atualizados.status

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar o cartão. Tente novamente mais tarde."
            )

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Dados atualizados com sucesso.",
            "data": CartaoResponse.from_model(cartao)
        }

    async def recarregar_cartao(self, recarga: CartaoRecarga, uuid: UUID) -> dict:
        query = await self.db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.uuid == uuid,
                )
            )
        )
        cartao = query.scalars().first()

        if cartao.status != StatusEnum.ATIVO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O cartão informado não está ativo."
            )

        cartao.saldo += recarga.valor

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recarregar o cartão. Tente novamente mais tarde."
            )

        return {
            "status_code": status.HTTP_200_OK,
            "message": f"O cartão foi recarregado em R${recarga.valor:.2f}.",
            "data": CartaoResponse.from_model(cartao)
        }

    async def transferir_saldo(self, transferencia: CartaoTransferir) -> dict:
            query = await self.db.execute(
                select(CartaoModel).where(
                    and_(
                        CartaoModel.uuid == transferencia.uuid_pagante,
                    )
                )
            )
            cartao = query.scalars().first()

            if cartao.status != StatusEnum.ATIVO:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O cartão do pagante não está ativo."
                )

            if transferencia.valor > cartao.saldo:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Saldo insuficiente. Saldo atual: R${cartao.saldo:.2f} | "
                           f"Transferência solicitada: R${transferencia.valor:.2f}."
                )

            cartao.saldo -= transferencia.valor

            query2 = await self.db.execute(
                select(CartaoModel).where(
                    and_(
                        CartaoModel.uuid == transferencia.uuid_recebente
                    )
                )
            )
            cartao2 = query2.scalars().first()

            if cartao2 is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cartão não encontrado, verifique o UUID do recebedor."
                )

            if cartao2.status != StatusEnum.ATIVO:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O cartão do recebedor não está ativo."
                )

            cartao2.saldo += transferencia.valor

            try:
                await self.db.commit()
            except Exception:
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao atualizar o cartão. Tente novamente mais tarde."
                )

            return {
                "status_code": status.HTTP_200_OK,
                "message": f"Foi transferido o valor de R${transferencia.valor:.2f} "
                           f"para o cartão do UUID ({cartao2.uuid}).",
                "data": CartaoResponse.from_model(cartao)
            }
