from fastapi import status

from app.schemas.cartao_schema import (
    CartaoResponseWrapper,
    CartoesPorCpfWrapper,
    CartaoUpdateWrapper,
    CartaoRecargaWrapper,
    CartaoTransferirWrapper,
)
from app.api.v1.endpoints.responses.cartao_responses import Responses


class RouteConfig:

    @staticmethod
    def solicitar_cartao():
        return {
            "response_model": CartaoResponseWrapper,
            "status_code": status.HTTP_201_CREATED,
            "summary": "Solicitar cartão",
            "description": "Gera um novo cartão para o usuário com base nas informações fornecidas.",
            "responses": {
                **Responses.SolicitarCartao.sucesso,
                **Responses.SolicitarCartao.erros_validacao
            }
        }

    @staticmethod
    def cartoes_por_cpf():
        return {
            "response_model": CartoesPorCpfWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Listar cartões por CPF",
            "description": "Retorna todos os cartões vinculados ao CPF informado.",
            "responses": {
                **Responses.CartoesPorCpf.sucesso,
                **Responses.CartoesPorCpf.cpf_invalido
            }
        }

    @staticmethod
    def atualizar_dados():
        return {
            "response_model": CartaoUpdateWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Atualizar dados do cartão",
            "description": "Atualiza os dados do cartão pertencente ao UUID informado.",
            "responses": {
                **Responses.AtualizarDados.sucesso,
                **Responses.AtualizarDados.uuid_invalido,
                **Responses.AtualizarDados.erros_validacao,
                **Responses.AtualizarDados.campos_invalidos,
            }
        }

    @staticmethod
    def recarregar_cartao():
        return {
            "response_model": CartaoRecargaWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Recarregar cartão",
            "description": "Recarrega o cartão pertencente ao UUID informado.",
            "responses": {
                **Responses.RecarregarCartao.sucesso,
                **Responses.RecarregarCartao.erros_validacao,
                **Responses.RecarregarCartao.uuid_invalido,
            }
        }

    @staticmethod
    def transferir_saldo():
        return {
            "response_model": CartaoTransferirWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Transferir saldo",
            "description": "Transfere saldo entre cartões por UUID.",
            "responses": {
                **Responses.TransferirSaldo.sucesso,
                **Responses.TransferirSaldo.erros_validacao,
            }
        }
