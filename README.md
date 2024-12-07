# API - Gerenciamento de Cartões de Crédito

## Descrição

Esta API oferece funcionalidades para o gerenciamento de cartões de crédito, permitindo a criação, atualização, recarga e transferência de saldo entre cartões, além de assegurar a proteção de dados sensíveis através de autenticação e segurança avançadas.

## Funcionalidades

- **Solicitação de Cartão:** Gera um novo cartão para o usuário, associando-o ao CPF, e-mail e nome do titular. Ao solicitar o cartão, é publicada uma mensagem para a fila de aprovação no RabbitMQ, que será processada e consumida quando o status do cartão ser alterado para "ATIVO".
- **Listar Cartões por CPF:** Permite consultar todos os cartões cadastrados e seus respectivos dados associados a um CPF específico.
- **Atualização de Dados do Cartão:** Atualiza dados como o nome do titular, endereço, status e e-mail de um cartão específico identificado pelo UUID. Ao alterar o status do cartão para "ATIVO", a rota envia um e-mail ao titular do cartão, informando o sucesso na ativação.
- **Recarregar Cartão:** Adiciona saldo ao cartão indicado pelo UUID, caso ele esteja ativo.
- **Transferência de Saldo:** Facilita a transferência de saldo entre dois cartões ativos, desde que haja saldo suficiente.

## Segurança e Autenticação

A API garante a segurança dos dados de cartões utilizando hash e criptografia, evitando o armazenamento direto de informações sensíveis, como número do cartão e CVV, no banco de dados. A autenticação é realizada via tokens JWT, permitindo que apenas usuários autenticados acessem recursos sensíveis e realizem operações de cartão.

## Estrutura do Projeto

```plaintext
api-cartoes/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── responses/
│   │   │   │   │   └── cartao_responses.py
│   │   │   │   ├── router_config/
│   │   │   │   │   └── config.py
│   │   │   │   └── cartao.py
│   │   │   └── api.py
│   ├── core/
│   │   ├── auth.py
│   │   ├── configs.py
│   │   └── deps.py
│   ├── database/
│   │   └── base.py
│   ├── migrations/
│   │   ├── versions/
│   │   │   └──8751d7daf025_adicionada_a_tabela_cartoes.py
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── models/
│   │   └── cartao_model.py
│   ├── schemas/
│   │   └── cartao_schema.py
│   ├── services/
│   │   ├── cartao_services.py
│   │   ├── rabbitmq_consumer.py
│   │   └── rabbitmq_publisher.py
│   ├── alembic.ini
│   └── main.py
├── tests/
│   └── services/
│       └── test_cartao_services.py
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── poetry.lock
└── pyproject.toml
```

## Como Usar

1- Clone este repositório:
   ```bash
   git clone https://github.com/lazzarusxd/api-cartoes.git
   ```


2- Navegue até o diretório do projeto:
   ```bash
   cd api-cartoes
   ```


3- Crie e execute os containers Docker necessários:
   ```bash
   docker-compose up --build
   ```


4- Crie seu ambiente de desenvolvimento e instale as dependências usando Poetry:
   ```bash
   poetry install
   ```


5- Execute seu ambiente de desenvolvimento com as dependências usando Poetry:
   ```bash
   poetry shell
   ```

  
6- Crie a tabela no banco de dados usando Alembic:
   ```bash
   docker exec -it api-cartoes-app-1 poetry run alembic upgrade head
   ```


7- Configure o interpretador Python na sua IDE:
- Caso seu ambiente de desenvolvimento tenha sido criado no WSL, selecione-o e escolha a opção "System Interpreter".
  
- Navegue até o diretório retornado no terminal após a execução do comando do Passo 5.
  
- Procure o executável do Python dentro do ambiente virtual.


8- Realize as requisições desejadas conforme o próximo tópico (Endpoints):
   - As informações sensíveis do arquivo ".env" são fictícias, portanto, solicite o arquivo original ou configure-o conforme suas necessidades.
     
   - Verifique as portas corretas dos serviços utilizando o aplicativo Docker Desktop ou o comando:

      ```bash
      docker ps
      ```
     
   - Acesse o RabbitMQ Management no host e porta correspondentes, e faça a criação dos seguintes itens:
     
     - Crie uma exchange com o nome "card_exchange" do tipo direct.
     - Crie uma queue com o nome "approval_queue" do tipo "default for virtual host", com o argumento "x-overflow" igual a "reject-publish". 
     - Realize o binding da fila "approval_queue" com a exchange "card_exchange" utilizando a routing key "approval_rk".


## Endpoints

### **Solicitação de Cartão**:

- ***Rota***: POST /solicitar_cartao
- ***Descrição***: Cria um novo cartão vinculado ao CPF e ao nome do titular.

**Exemplo de entrada:**

```plaintext
{
  "titular_cartao": "JOAO DA SILVA",
  "cpf_titular": "12345678912",
  "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
  "email": "JOAODASILVA@EMAIL.COM"
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 201,
  "message": "Cartão criado com sucesso.",
  "data": {
    "titular_cartao": "JOAO DA SILVA",
    "cpf_titular": "12345678912",
    "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
    "status": "EM_ANALISE",
    "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
  }
}
```

### **Listar cartões por CPF (requer autenticação)**:

- ***Rota***: GET /listar_cartoes/cpf/{cpf_titular}
- ***Descrição***: Lista os cartões vinculados ao CPF do titular.

**Exemplo de entrada:**

```plaintext
URL http://localhost:8000/api/v1/cartoes/listar_cartoes/cpf/12345678912
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 200,
  "message": "Todos os cartões foram listados com sucesso.",
  "data": {
    "cartoes": [
      {
        "uuid": "9534299a-8c90-473d-b9c6-cc2bb18103ae",
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345678912",
        "status": "EM_ANALISE",
        "email": "JOAODASILVA@EMAIL.COM",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
        "saldo": 50,
        "numero_cartao": "1111222233334444",
        "cvv": "123",
        "expiracao": "10/2029",
        "data_criacao": "16/10/2024 11:25:09",
        "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
      },
      {
        "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
        "titular_cartao": "JOAO DA SILVA",
        "cpf_titular": "12345678912",
        "status": "EM_ANALISE",
        "email": "JOAODASILVA@EMAIL.COM",
        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
        "saldo": 150,
        "numero_cartao": "4444333322221111",
        "cvv": "321",
        "expiracao": "10/2029",
        "data_criacao": "16/10/2024 11:24:47",
        "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
      }
    ]
  }
}
```

### **Atualizar Dados do Cartão (requer autenticação)**:

- ***Rota***: PUT /atualizar_dados/{uuid}
- ***Descrição***: Atualiza as informações de um cartão existente, como o titular e o endereço.

**Exemplo de entrada:**

```plaintext
URL http://localhost:8000/api/v1/cartoes/atualizar_dados/fb1d729b-46f7-4b2d-8b29-73eedc149e24
{
  "titular_cartao": "JOAO DA SILVA",
  "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
  "status": "ATIVO",
  "email": "JOAODASILVA22@EMAIL.COM"
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "detail": {
    "status_code": 200,
    "message": "Dados atualizados com sucesso.",
    "data": {
      "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
      "titular_cartao": "JOAO DA SILVA",
      "cpf_titular": "12345678912",
      "status": "ATIVO",
      "email": "JOAODASILVA22@EMAIL.COM",
      "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
      "saldo": 50,
      "numero_cartao": "4444333322221111",
      "cvv": "321",
      "expiracao": "10/2029",
      "data_criacao": "16/10/2024 11:24:47",
      "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
    }
  }
}
```

### **Recarregar Cartão (requer autenticação)**:

- ***Rota***: POST /recarregar_cartao/{uuid}
- ***Descrição***: Recarrega o saldo de um cartão específico.

**Exemplo de entrada:**

```plaintext
URL http://localhost:8000/api/v1/cartoes/atualizar_dados/fb1d729b-46f7-4b2d-8b29-73eedc149e24
{
  "valor": 10
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "detail": {
    "status_code": 200,
    "message": "O cartão foi recarregado em R$10.00.",
    "data": {
      "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
      "titular_cartao": "JOAO DA SILVA",
      "cpf_titular": "12345678912",
      "status": "ATIVO",
      "email": "JOAODASILVA@EMAIL.COM",
      "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
      "saldo": 10,
      "numero_cartao": "4444333322221111",
      "cvv": "321",
      "expiracao": "10/2029",
      "data_criacao": "16/10/2024 11:24:47",
      "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
    }
  }
}
```

### **Transferência de Saldo (requer autenticação)**:

- ***Rota***: POST /transferir_saldo
- ***Descrição***: Realiza a transferência de saldo entre dois cartões.

**Exemplo de entrada:**

```plaintext
{
  "uuid_pagante": "1dac2271-04a0-23az-8p5g-71ec292acbbb",
  "uuid_recebente": "4ddde01x-10zz-41c9-j3eg-0nbw2e4a2ja7",
  "valor": 200
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "detail": {
    "status_code": 200,
    "message": "Foi transferido o valor de R$200.00 para o cartão do UUID (4ddde01x-10zz-41c9-j3eg-0nbw2e4a2ja7).",
    "data": {
      "uuid": "8fdb9279-03c0-44fb-8e5e-74ec164acfdf",
      "titular_cartao": "JOAO DA SILVA",
      "cpf_titular": "12345678912",
      "status": "ATIVO",
      "email": "JOAODASILVA@EMAIL.COM",
      "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
      "saldo": 50,
      "numero_cartao": "4444333322221111",
      "cvv": "321",
      "expiracao": "10/2029",
      "data_criacao": "16/10/2024 11:24:47",
      "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
    }
  }
}
```

### **Possíveis Erros**:

- ***400***: Erros de validação ou ao processar solicitações.Erros de validação ou ao processar solicitações.
- ***404***: Cartão não encontrado para o CPF ou UUID informado.
- ***422***: Erros relacionados a parâmetros enviados, como valor ou UUID inválido.
- ***500***: Erro interno do servidor ao processar a requisição.



## Contato:

João Lázaro - joaolazarofera@gmail.com

Link do projeto - https://github.com/lazzarusxd/api-cartoes
