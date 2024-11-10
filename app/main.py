from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.configs import settings
from app.api.v1.api import router

load_dotenv()

app = FastAPI(
    title="API de Gerenciamento de Cartões",
    description="""
    Esta API é responsável pelo gerenciamento de cartões de crédito, permitindo a solicitação, atualização, recarga e transferência de saldo entre cartões. Além disso, a API oferece funcionalidades de autenticação e segurança para proteger os dados dos usuários.

    Funcionalidades disponíveis:

    - Solicitação de Cartão: Gera um novo cartão de crédito para um usuário, associando-o ao CPF e ao nome do titular fornecidos.
    - Listar Cartões por CPF: Recupera todos os cartões cadastrados no banco, associados ao CPF informado.
    - Atualizar Dados do Cartão: Permite atualizar informações como o nome do titular, o endereço e o status (apenas do cartão do UUID), de todos os cartões vinculados ao UUID informado.
    - Recarregar Cartão: Permite recarregar um cartão com um valor específico, informando o UUID do cartão a ser recarregado, desde o cartão esteja ativo.
    - Transferência de Saldo: Permite transferir saldo de um cartão para outro, desde que ambos os cartões estejam ativos e o saldo seja suficiente.

    Autenticação e Segurança:

    A API não armazena dados sensíveis como número de cartão e CVV diretamente no banco de dados. Em vez disso, utiliza técnicas de criptografia e hash para garantir a segurança dos dados, incluindo a validação do CPF e do nome do titular. Além disso, a autenticação é realizada através de tokens JWT, garantindo que apenas usuários autenticados possam acessar os recursos sensíveis.

    Endpoints disponíveis:

    - POST /solicitar_cartao: Solicita um novo cartão para um usuário.
    - GET /listar_cartoes/cpf/{cpf_titular}: Lista os cartões vinculados ao CPF do titular.
    - PUT /atualizar_dados/{uuid}: Atualiza informações de um cartão existente, como o titular e o endereço.
    - POST /recarregar_cartao/{uuid}: Recarrega o saldo de um cartão específico.
    - POST /transferir_saldo: Realiza a transferência de saldo entre dois cartões.

    Possíveis erros:

    - 400: Erros de validação ou ao processar solicitações.
    - 404: Cartão não encontrado para o CPF ou UUID informado.
    - 422: Erros relacionados a parâmetros enviados, como valor ou UUID inválido.
    - 500: Erro interno do servidor ao processar a requisição.
    """,
    version="1.1"
)

app.include_router(router, prefix=settings.API_V1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level='debug', reload=True)
