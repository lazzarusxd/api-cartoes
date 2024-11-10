import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import HTTPException, status

from app.main import app
from app.models.cartao_model import StatusEnum


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_solicitar_cartao(mocker, client):
    mock_cartao_service = mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao"
    )

    dados_cartao = {
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345678912",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mock_cartao_service.return_value = {
        "status_code": 201,
        "message": "Cartão criado com sucesso.",
        "data": {
            "titular_cartao": dados_cartao["titular_cartao"].upper(),
            "cpf_titular": dados_cartao["cpf_titular"],
            "endereco": dados_cartao["endereco"].upper(),
            "status": StatusEnum.EM_ANALISE,
            "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
        }
    }

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data["message"] == "Cartão criado com sucesso."
    assert response_data["data"]["titular_cartao"] == dados_cartao["titular_cartao"].upper()
    assert response_data["data"]["cpf_titular"] == dados_cartao["cpf_titular"]
    assert response_data["data"]["endereco"] == dados_cartao["endereco"].upper()
    assert response_data["data"]["token"] == "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"


@pytest.mark.asyncio
async def test_solicitar_cartao_nome_titular_somente_letras(mocker, client):
    dados_cartao = {
        "titular_cartao": "JOAO DA SILV2",
        "cpf_titular": "12345678912",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome do titular deve ser composto apenas por letras."
        )
    )

    response = await client.post("/api/v1/cartoes/solicitar_cartao", json=dados_cartao)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "O nome do titular deve ser composto apenas por letras."


@pytest.mark.asyncio
async def test_solicitar_cartao_nome_vazio(mocker, client):
    dados_cartao = {
        "titular_cartao": "",
        "cpf_titular": "12345678912",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome titular é um campo obrigatório e não pode ser uma string vazia."
        )
    )

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Nome titular é um campo obrigatório e não pode ser uma string vazia."


@pytest.mark.asyncio
async def test_solicitar_cartao_endereco_vazio(mocker, client):
    dados_cartao = {
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345678912",
        "endereco": ""
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Endereço é um campo obrigatório e não pode ser uma string vazia."
        )
    )

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Endereço é um campo obrigatório e não pode ser uma string vazia."


@pytest.mark.asyncio
async def test_solicitar_cartao_cpf_invalido_letras(mocker, client):
    dados_cartao = {
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345abc912",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O CPF deve conter apenas números."
        )
    )

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "O CPF deve conter apenas números."


@pytest.mark.asyncio
async def test_solicitar_cartao_cpf_tamanho_invalido(mocker, client):
    dados_cartao = {
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "1234567",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O CPF deve conter exatamente 11 dígitos."
        )
    )

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "O CPF deve conter exatamente 11 dígitos."


@pytest.mark.asyncio
async def test_solicitar_cartao_cpf_vazio(mocker, client):
    dados_cartao = {
        "titular_cartao": "JOÃO DA SILVA",
        "cpf_titular": "",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    mocker.patch(
        "app.services.cartao_services.CartaoServices.solicitar_cartao",
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF é um campo obrigatório e não pode ser uma string vazia."
        )
    )

    response = await client.post(
        "/api/v1/cartoes/solicitar_cartao",
        json=dados_cartao
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "CPF é um campo obrigatório e não pode ser uma string vazia."


@pytest.mark.asyncio
async def test_solicitar_cartao_cpf_nome_diferente():
    dados_cartao1 = {
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345678912",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA"
    }

    dados_cartao2 = {
        "titular_cartao": "MARIA OLIVEIRA",
        "cpf_titular": "12345678912",
        "endereco": "RUA DO SOL, BAIRRO ESPERANÇA"
    }

    cartoes_cadastrados = {}

    def mock_consultar_cartao(cpf_titular):
        return cartoes_cadastrados.get(cpf_titular, [])

    async def mock_solicitar_cartao(dados):
        usuarios_existentes = mock_consultar_cartao(dados["cpf_titular"])

        for usuario in usuarios_existentes:
            if usuario["titular_cartao"].upper() != dados["titular_cartao"].upper():
               raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já cadastrado para um titular diferente."
                )

        cartoes_cadastrados[dados["cpf_titular"]] = [
            {
                "titular_cartao": dados["titular_cartao"].upper(),
                "cpf_titular": dados["cpf_titular"]
            }
        ]

        return {
            "status_code": 201,
            "message": "Cartão criado com sucesso.",
            "data": {
                "titular_cartao": dados["titular_cartao"].upper(),
                "cpf_titular": dados["cpf_titular"],
                "endereco": dados["endereco"].upper(),
                "status": "EM_ANALISE",
                "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
            }
        }

    response_data = await mock_solicitar_cartao(dados_cartao1)
    assert response_data["status_code"] == 201
    assert response_data["message"] == "Cartão criado com sucesso."

    try:
        await mock_solicitar_cartao(dados_cartao2)
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "CPF já cadastrado para um titular diferente."
