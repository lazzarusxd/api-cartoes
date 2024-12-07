from uuid import UUID

from fastapi import APIRouter, Depends, Path
from app.services.cartao_services import CartaoServices
from app.core.deps import (
    auth_cartoes_por_cpf,
    auth_atualizar_informacoes,
    auth_recarregar_cartao,
    auth_transferir_saldo
)
from app.schemas.cartao_schema import (
    CartaoRequest,
    CartaoUpdate,
    CartaoRecarga,
    CartaoTransferir,
    CartaoResponseWrapper,
    CartoesPorCpfWrapper,
    CartaoUpdateWrapper,
    CartaoRecargaWrapper,
    CartaoTransferirWrapper
)
from app.api.v1.endpoints.router_config.config import RouteConfig

router = APIRouter()


@router.post("/solicitar_cartao", **RouteConfig.solicitar_cartao())
async def solicitar_cartao(
        dados_cartao: CartaoRequest,
        cartao_services: CartaoServices = Depends()
) -> CartaoResponseWrapper:
    cartao_response = await cartao_services.solicitar_cartao(
        dados_cartao,
        exchange="card_exchange",
        routing_key="approval_rk"
    )

    return CartaoResponseWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.get("/listar_cartoes/cpf/{cpf_titular}", **RouteConfig.cartoes_por_cpf())
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


@router.put("/atualizar_dados/{uuid}", **RouteConfig.atualizar_dados())
async def atualizar_dados(
        dados_atualizados: CartaoUpdate,
        uuid: UUID = Depends(auth_atualizar_informacoes),
        cartao_services: CartaoServices = Depends()
) -> CartaoUpdateWrapper:
    cartao_response = await cartao_services.atualizar_dados(
        dados_atualizados,
        uuid,
        queue="approval_queue"
    )

    return CartaoUpdateWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.post("/recarregar_cartao/{uuid}", **RouteConfig.recarregar_cartao())
async def recarregar_cartao(
        uuid: UUID = Path(title="UUID do cartão", description="UUID do cartão a ser recarregado."),
        recarga: CartaoRecarga = Depends(auth_recarregar_cartao),
        cartao_services: CartaoServices = Depends()
) -> CartaoRecargaWrapper:
    cartao_response = await cartao_services.recarregar_cartao(recarga, uuid)

    return CartaoRecargaWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.post("/transferir_saldo", **RouteConfig.transferir_saldo())
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
