# tcc

# README.md

Este documento descreve os passos para configurar e executar um projeto Django com integração de variáveis de ambiente e APIs do Google.

---

## 📋 Sumário

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Ambiente Virtual](#configuração-do-ambiente-virtual)
3. [Instalação de Dependências](#instalação-de-dependências)
4. [Configuração de Variáveis de Ambiente](#configuração-de-variáveis-de-ambiente)
5. [Migrações e Banco de Dados](#migrações-e-banco-de-dados)
6. [Execução do Servidor de Desenvolvimento](#execução-do-servidor-de-desenvolvimento)
7. [Licença](#licença)

---

## Pré-requisitos
* **Python 3.x** instalado
---

## Configuração do Ambiente Virtual

1. Instale o `pip` (caso ainda não exista):

   ```bash
   sudo apt install python3-pip
   ```

2. Crie e ative o ambiente virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

---

## Instalação de Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias:

```bash
pip3 install django
pip3 install python-dotenv
pip3 install google-api-python-client
pip3 install django-cors-headers
```

## Configuração de Variáveis de Ambiente

1. Crie um arquivo `.env` na raiz do projeto.

2. Adicione a variável:
   
   ```env
   YOUTUBE_API_KEY=INSIRA_SUA_CHAVE_AQUI
   ```
---

## Migrações e Banco de Dados

Execute os comandos de migração para criar as tabelas no banco de dados:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

> 🔍 Se precisar criar superusuário, use:
>
> ```bash
> python3 manage.py createsuperuser
> ```

---

## Execução do Servidor de Desenvolvimento

Inicie o servidor local:

```bash
python3 manage.py runserver
```

---
## Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).

---
