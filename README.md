# CryptaBank

**CryptaBank** é um CTF baseado em um sistema bancário, composto por uma aplicação web e um serviço bancário acessível através de um protocolo próprio.

O projeto possui duas interfaces de interação: a aplicação web e um cliente de terminal desenvolvido em Python para comunicação direta com o serviço bancário.

## Requisitos

* [Docker](https://docs.docker.com/get-docker/) com Docker Compose
* Python **3.12+** para executar o cliente de terminal localmente

## Instalação

Clone o repositório e entre no diretório:

```bash
git clone https://github.com/batata902/termbank.git
cd termbank
```

Inicie os serviços:

```bash
docker compose up --build
```

Após a inicialização:

| Serviço          | Endereço                |
| ---------------- | ----------------------- |
| Aplicação web    | `http://localhost:5000` |
| Serviço bancário | `localhost:9000`        |

## Cliente de terminal

O cliente permite interagir diretamente com o serviço bancário através do protocolo utilizado pelo sistema.

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Com os serviços em execução:

```bash
python cli/client.py localhost 9000
```

## Acesso inicial

```text
Usuário: guest
Senha: senhadaora
```

## Persistência

O banco de dados utilizado pelo serviço é armazenado em:

```text
bank/src/database/database.db
```

O arquivo é montado como bind mount pelo Docker Compose, mantendo os dados entre reinicializações dos containers.

Para resetar o ambiente:

```bash
docker compose down
rm bank/src/database/database.db
```

Na próxima inicialização, o banco será criado novamente.

## Encerrando o ambiente

Para parar os serviços:

```bash
docker compose down
```

Para reconstruir as imagens após alterações:

```bash
docker compose up --build
```

## Estrutura

```text
termbank/
├── bank/                  # Serviço bancário
├── cli/                   # Cliente de terminal
├── web/                   # Aplicação web
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

## CryptaBank

O ambiente explora diferentes superfícies de ataque entre a aplicação web, o protocolo do serviço bancário e a lógica responsável pelas operações da conta.
