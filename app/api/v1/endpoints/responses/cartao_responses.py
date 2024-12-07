class Responses:

    class SolicitarCartao:
        sucesso = {
            201: {
                "description": "Cartão criado com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
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
                    }
                }
            }
        }

        erros_validacao = {
            400: {
                "description": "Erro de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O nome do titular deve ser composto apenas por letras.",
                                "Nome titular é um campo obrigatório e não pode ser uma string vazia.",
                                "Endereço é um campo obrigatório e não pode ser uma string vazia.",
                                "CPF é um campo obrigatório e não pode ser uma string vazia.",
                                "O CPF deve conter apenas números.",
                                "O CPF deve conter exatamente 11 dígitos.",
                                "CPF já cadastrado para um titular diferente.",
                                "E-mail é um campo obrigatório e não pode ser uma string vazia."
                            ]
                        }
                    }
                }
            }
        }

    class CartoesPorCpf:
        sucesso = {
            200: {
                "description": "Todos os cartões foram listados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
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
                                        "saldo": 50.0,
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
                                        "saldo": 150.0,
                                        "numero_cartao": "4444333322221111",
                                        "cvv": "321",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:24:47",
                                        "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

        cpf_invalido = {
            404: {
                "description": "Erro no path. O CPF informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "O CPF informado não foi encontrado."
                        }
                    }
                }
            }
        }

    class AtualizarDados:
        sucesso = {
            200: {
                "description": "Dados atualizados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "status_code": 200,
                                "message": "Dados atualizados com sucesso.",
                                "data": {
                                    "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
                                    "titular_cartao": "JOAO DA SILVA",
                                    "cpf_titular": "12345678912",
                                    "status": "ATIVO",
                                    "email": "JOAODASILVA@EMAIL.COM",
                                    "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                    "saldo": 50.0,
                                    "numero_cartao": "4444333322221111",
                                    "cvv": "321",
                                    "expiracao": "10/2029",
                                    "data_criacao": "16/10/2024 11:24:47",
                                    "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                                }
                            }
                        }
                    }
                }
            }
        }

        erros_validacao = {
            400: {
                "description": "Erro de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "Nenhum campo para atualizar foi fornecido.",
                                "O nome do titular não pode ser uma string vazia.",
                                "O nome do titular deve ser composto apenas por letras.",
                                "Endereço inválido. O endereço não pode ser vazio.",
                                "O status não pode ser uma string vazia.",
                                "O status fornecido deve ser do tipo StatusEnum.",
                                "E-mail é um campo obrigatório e não pode ser uma string vazia."
                            ]
                        }
                    }
                }
            }
        }

        uuid_invalido = {
            404: {
                "description": "Erro no path. O UUID informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Cartão não encontrado, verifique o UUID."
                        }
                    }
                }
            }
        }

        campos_invalidos = {
            422: {
                "description": "Erro. Atributo não encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                {
                                    "type": "extra_forbidden",
                                    "loc": [
                                        "body",
                                        "statu"
                                    ],
                                    "msg": "Extra inputs are not permitted",
                                    "input": "ATIVO"
                                }
                            ]
                        }
                    }
                }
            }
        }

    class RecarregarCartao:
        sucesso = {
            200: {
                "description": "Recarga efetuada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
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
                                    "saldo": 10.0,
                                    "numero_cartao": "4444333322221111",
                                    "cvv": "321",
                                    "expiracao": "10/2029",
                                    "data_criacao": "16/10/2024 11:24:47",
                                    "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                                }
                            }
                        }
                    }
                }
            }
        }

        erros_validacao = {
            400: {
                "description": "Erro de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O valor da recarga deve ser um número válido.",
                                "O valor da recarga deve ser maior do que 0.",
                                "O cartão informado não está ativo."
                            ]
                        }
                    }
                }
            }
        }

        uuid_invalido = {
            404: {
                "description": "Erro no path. O UUID informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Cartão não encontrado, verifique o UUID."
                        }
                    }
                }
            }
        }

    class TransferirSaldo:
        sucesso = {
            200: {
                "description": "Transferência efetuada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "status_code": 200,
                                "message": "Foi transferido o valor de R$200.00 para o cartão do "
                                           "UUID (4ddde01x-10zz-41c9-j3eg-0nbw2e4a2ja7).",
                                "data": {
                                    "uuid": "8fdb9279-03c0-44fb-8e5e-74ec164acfdf",
                                    "titular_cartao": "JOAO DA SILVA",
                                    "cpf_titular": "12345678912",
                                    "status": "ATIVO",
                                    "email": "JOAODASILVA@EMAIL.COM",
                                    "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                    "saldo": 50.0,
                                    "numero_cartao": "4444333322221111",
                                    "cvv": "321",
                                    "expiracao": "10/2029",
                                    "data_criacao": "16/10/2024 11:24:47",
                                    "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                                }
                            }
                        }
                    }
                }
            }
        }

        erros_validacao = {
            400: {
                "description": "Erro de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O valor da recarga deve ser um número válido.",
                                "O valor da recarga deve ser maior do que 0.",
                                "O cartão do pagante não está ativo.",
                                "O cartão do recebedor não está ativo.",
                                "Cartão não encontrado, verifique o UUID do pagante.",
                                "Cartão não encontrado, verifique o UUID do recebedor.",
                                "Saldo insuficiente.Saldo atual: R$250.00 | Transferência solicitada: R$300.00."
                            ]
                        }
                    }
                }
            }
        }
