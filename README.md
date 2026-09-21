# CryptaBank

**CryptaBank** é um CTF baseado em uma aplicação bancária fictícia. O projeto combina uma **aplicação web** com um **serviço bancário acessível por protocolo próprio**, permitindo que os desafios sejam explorados através de diferentes interfaces.

O ambiente é executado com Docker Compose e também inclui um cliente de terminal em Python para interação direta com o serviço bancário.

## Requisitos

* [Docker](https://docs.docker.com/get-docker/) com Docker Compose
* Python **3.12+**, caso queira executar o cliente de terminal localmente

## Instalação

Clone o repositório e entre no diretório do projeto:

```bash
git clone https://github.com/batata902/termbank.git
cd termbank
```

Em seguida, construa as imagens e inicie os serviços:

```bash
docker compose up --build
```

Após a inicialização, os serviços estarão disponíveis em:

| Serviço          | Endereço                |
| ---------------- | ----------------------- |
| Aplicação web    | `http://localhost:5000` |
| Serviço bancário | `localhost:9000`        |

## Cliente de terminal

O projeto possui um cliente de terminal em Python para interagir diretamente com o serviço bancário.

Para executá-lo localmente, instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Com os serviços do Docker Compose em execução, inicie o cliente:

```bash
python cli/client.py localhost 9000
```

## Credenciais iniciais

O ambiente inclui uma conta para o primeiro acesso:

```text
Usuário: guest
Senha: senhadaora
```

> **Nota:** essas credenciais fazem parte do ambiente do CTF e não representam credenciais reais.

## Persistência dos dados

O banco de dados local é armazenado em:

```text
bank/src/database/database.db
```

Esse diretório é montado como um **bind mount** pelo Docker Compose, permitindo que os dados do banco persistam mesmo após os containers serem encerrados.

Para remover os dados e iniciar o ambiente novamente do zero, primeiro pare os containers:

```bash
docker compose down
```

Depois remova o arquivo:

```text
bank/src/database/database.db
```

Na próxima inicialização, o banco será recriado pelo ambiente.

## Encerrando o ambiente

Para parar os containers:

```bash
docker compose down
```

Para reconstruir as imagens após alterações no projeto:

```bash
docker compose up --build
```

## Estrutura do projeto

```text
termbank/
├── bank/       # Aplicação e serviço bancário
├── cli/        # Cliente de terminal
├── ...
├── docker-compose.yml
└── requirements.txt
```

## Sobre o CTF

O CryptaBank foi desenvolvido como um ambiente de laboratório para explorar vulnerabilidades e comportamentos relacionados a uma aplicação bancária fictícia.

