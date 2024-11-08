from uuid import UUID

from fastapi import APIRouter, status, Depends, Path

from app.api.v1.endpoints.responses.cartao_responses import Responses
from app.services.cartao_services import CartaoServices
from app.core.deps import (auth_cartoes_por_cpf, auth_atualizar_informacoes,
                           auth_transferir_saldo, auth_recarregar_cartao)
from app.schemas.cartao_schema import (CriarCartao, CartaoResponseWrapper, CartoesPorCpfWrapper, CartaoUpdate,
                                       CartaoUpdateWrapper, CartaoTransferir, CartaoTransferirWrapper,
                                       CartaoRecargaWrapper, CartaoRecarga)

router = APIRouter()


@router.post(
    "/solicitar_cartao",
    response_model=CartaoResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar cartão",
    description="Gera um novo cartão para o usuário com base nas informações fornecidas.",
    responses={
        **Responses.SolicitarCartao.sucesso,
        **Responses.SolicitarCartao.erros_validacao
    }
)
async def solicitar_cartao(
        dados_cartao: CriarCartao,
        cartao_services: CartaoServices = Depends()
) -> CartaoResponseWrapper:
    cartao_response = await cartao_services.solicitar_cartao(dados_cartao)

    return CartaoResponseWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.get(
    "/listar_cartoes/cpf/{cpf_titular}",
    response_model=CartoesPorCpfWrapper,
    status_code=status.HTTP_200_OK,
    summary="Listar cartões por CPF",
    description="Retorna todos os cartões vinculados ao CPF informado.",
    responses={
        **Responses.CartoesPorCpf.sucesso,
        **Responses.CartoesPorCpf.cpf_invalido
    }
)
async def cartoes_por_cpf(
        cpf_titular: str = Depends(auth_cartoes_por_cpf),
        cartao_services: CartaoServices = Depends()
) -> CartoesPorCpfWrapper:
    cartao_response = await cartao_services.cartoes_por_cpf(cpf_titular)

    return CartoesPorCpfWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.put(
    "/atualizar_dados/{uuid}",
    response_model=CartaoUpdateWrapper,
    status_code=status.HTTP_200_OK,
    summary="Atualizar dados do cartão",
    description="Atualiza os dados do cartão pertencente ao UUID informado.",
    responses={
        **Responses.AtualizarDados.sucesso,
        **Responses.AtualizarDados.uuid_invalido,
        **Responses.AtualizarDados.erros_validacao
    }
)
async def atualizar_dados(
        dados_atualizados: CartaoUpdate,
        uuid: UUID = Depends(auth_atualizar_informacoes),
        cartao_services: CartaoServices = Depends()
) -> CartaoUpdateWrapper:
    cartao_response = await cartao_services.atualizar_info(dados_atualizados, uuid)

    return CartaoUpdateWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.post(
    "/recarregar_cartao/{uuid}",
    response_model=CartaoRecargaWrapper,
    status_code=status.HTTP_200_OK,
    summary="Recarregar cartão",
    description="Recarrega o cartão pertencente ao UUID informado.",
    responses={
        **Responses.RecarregarCartao.sucesso,
        **Responses.RecarregarCartao.erros_validacao,
        **Responses.RecarregarCartao.uuid_invalido
    }
)
async def recarregar_cartao(
        uuid: UUID = Path(
            title="UUID do cartão",
            description="UUID do cartão a ser recarregado."
        ),
        recarga: CartaoRecarga = Depends(auth_recarregar_cartao),
        cartao_services: CartaoServices = Depends()
) -> CartaoRecargaWrapper:
    cartao_response = await cartao_services.recarregar_cartao(recarga, uuid)

    return CartaoRecargaWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.post(
    "/transferir_saldo",
    response_model=CartaoTransferirWrapper,
    status_code=status.HTTP_200_OK,
    summary="Transferir saldo",
    description="Transfere saldo entre cartões por UUID.",
    responses={
        **Responses.TransferirSaldo.sucesso,
        **Responses.TransferirSaldo.erros_validacao
    }
)
async def transferir_saldo(
        transferencia: CartaoTransferir = Depends(auth_transferir_saldo),
        cartao_services: CartaoServices = Depends()
) -> CartaoTransferirWrapper:
    cartao_response = await cartao_services.transferir_saldo(transferencia)

    return CartaoTransferirWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )
