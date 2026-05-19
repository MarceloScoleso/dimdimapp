# 🏦 DimDimApp - CP3 DevOps

> **Sistema de Gestão de Clientes** conteinerizado com Docker, conectado a um banco PostgreSQL, hospedado em ambiente de nuvem (Azure VM).

---

## 👥 Equipe

| Nome                                | RM     | Função        |
|-------------------------------------|--------|---------------|
| Marcelo Antônio Scoleso Júnior      | 557481 | Representante |
| João Paulo Francisco de Oliveira    | 557410 | Integrante    |

🔗 **Vídeo no YouTube:** https://www.youtube.com/watch?v=jGZZfUZW6HQ
🔗 **Repositório:** https://github.com/MarceloScoleso/dimdimapp

---

## 📋 Sobre o projeto

Aplicação web Full MVC desenvolvida em **Python (Flask)** que realiza um CRUD completo de clientes, conectada a um banco **PostgreSQL** com volume nomeado para persistência de dados. Toda a solução roda em dois containers Docker isolados em uma rede própria, em uma máquina virtual do Azure.

### Stack utilizada

- 🐍 **Python 3.11** + **Flask 3** (aplicação web MVC)
- 🐘 **PostgreSQL 16** (banco de dados)
- 🐳 **Docker** (conteinerização via Dockerfile)
- ☁️ **Azure Virtual Machine** (Ubuntu Server 22.04 LTS)

### Arquitetura

```
┌─────────────────────────── Azure VM (Ubuntu) ───────────────────────────┐
│                                                                          │
│   ┌──────────────── Rede Docker: dimdim-net-557481 ───────────────┐    │
│   │                                                                  │    │
│   │   ┌────────────────────┐         ┌────────────────────────┐    │    │
│   │   │  app-dimdim-557481 │ ──────► │  db-dimdim-557481      │    │    │
│   │   │  (Flask + Gunicorn)│         │  (PostgreSQL 16)       │    │    │
│   │   │  Porta 5000        │         │  Porta 5432            │    │    │
│   │   │  Usuário: dimdimuser│        │  Volume: dimdim-data   │    │    │
│   │   └────────────────────┘         └────────────────────────┘    │    │
│   │            ▲                                ▲                    │    │
│   └────────────│────────────────────────────────│───────────────────┘    │
│                │                                                          │
│           Porta 80 (NAT)                                                  │
└────────────────│──────────────────────────────────────────────────────────┘
                 │
            🌐 Internet
```

---

## 🚀 How-To: Execução do projeto do zero

### Pré-requisitos

- Conta ativa no Azure
- Cliente SSH no computador local
- Acesso à internet

---

### PARTE 1 — Criação da VM no Azure

1. Acesse o portal: https://portal.azure.com
2. No menu lateral, vá em **Virtual Machines** → **+ Create** → **Azure virtual machine**
3. Configure os campos:

   | Campo                 | Valor                                       |
   |-----------------------|---------------------------------------------|
   | Subscription          | Azure for Students                          |
   | Resource Group        | `rg-dimdim-557481` (criar novo)             |
   | Virtual machine name  | `vm-dimdim-557481`                          |
   | Region                | (uma das permitidas pela sua subscription)  |
   | Image                 | Ubuntu Server 22.04 LTS - x64 Gen2          |
   | Size                  | Standard_B2s ou Standard_D2s_v5             |
   | Authentication type   | SSH public key                              |
   | Username              | `azureuser`                                 |
   | Inbound ports         | SSH (22), HTTP (80)                         |

4. Em **Networking**, garanta que estão liberadas:
   - Porta **22** (SSH)
   - Porta **80** (HTTP) — para acessar a aplicação pelo navegador

5. Clique em **Review + create** → **Create**.
6. Baixe a chave SSH privada (`.pem`).
7. Aguarde alguns minutos até a VM estar "Running" e copie o **IP público**.

---

### PARTE 2 — Conectar na VM via SSH

```bash
# No terminal do seu computador (Linux/Mac/WSL/Git Bash)
chmod 600 vm-dimdim-557481_key.pem
ssh -i vm-dimdim-557481_key.pem azureuser@IP_PUBLICO_DA_VM
```

---

### PARTE 3 — Instalar o Docker na VM

Já conectado na VM, execute os comandos abaixo:

```bash
# Atualiza o sistema
sudo apt update && sudo apt upgrade -y

# Instala pré-requisitos
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Adiciona o repositório oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instala o Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Adiciona seu usuário ao grupo docker (para não precisar usar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Testa
docker --version
```

---

### PARTE 4 — Clonar o repositório

```bash
git clone https://github.com/MarceloScoleso/dimdimapp.git
cd dimdimapp
```

---

### PARTE 5 — Criar a rede Docker

```bash
docker network create dimdim-net-557481
```

Verifique:
```bash
docker network ls
```

---

### PARTE 6 — Criar o volume nomeado (persistência do banco)

```bash
docker volume create dimdim-data-557481
```

Verifique:
```bash
docker volume ls
```

---

### PARTE 7 — Subir o container do banco (PostgreSQL)

> ⚠️ Container do banco usa **imagem pública** (sem Dockerfile próprio).

```bash
docker container run -d \
  --name db-dimdim-557481 \
  --network dimdim-net-557481 \
  -v dimdim-data-557481:/var/lib/postgresql/data \
  -e POSTGRES_DB=dimdimdb \
  -e POSTGRES_USER=dimdim \
  -e POSTGRES_PASSWORD=dimdim123 \
  -p 5432:5432 \
  postgres:16
```

Acompanhe os logs até ver `database system is ready to accept connections`:
```bash
docker logs -f db-dimdim-557481
```

(Pressione `Ctrl+C` para sair dos logs.)

---

### PARTE 8 — Construir a imagem da aplicação (Dockerfile)

```bash
docker build -t dimdimapp-557481:1.0 .
```

Confira:
```bash
docker images | grep dimdimapp
```

---

### PARTE 9 — Subir o container da aplicação

```bash
docker container run -d \
  --name app-dimdim-557481 \
  --network dimdim-net-557481 \
  -e DB_HOST=db-dimdim-557481 \
  -e DB_PORT=5432 \
  -e DB_NAME=dimdimdb \
  -e DB_USER=dimdim \
  -e DB_PASSWORD=dimdim123 \
  -p 80:5000 \
  dimdimapp-557481:1.0
```

Acompanhe os logs (espere ver `[init_db] Tabela 'clientes' pronta`):
```bash
docker logs -f app-dimdim-557481
```

---

### PARTE 10 — Acessar a aplicação

No navegador do seu computador, acesse:

```
http://IP_PUBLICO_DA_VM
```

Você verá a tela inicial do **DimDimApp** com a lista de clientes vazia.

---

### 1. Containers rodando em background

```bash
docker container ls
```

### 2. Estrutura de diretórios e usuário não-root (app)

```bash
docker container exec -it app-dimdim-557481 bash
```

Dentro do container:
```bash
whoami       # → dimdimuser  (não-root!)
pwd          # → /dimdim
ls -la       # mostra os arquivos do projeto
exit
```

### 3. Estrutura do container do banco

```bash
docker container exec -it db-dimdim-557481 bash
whoami       # → root (normal para o postgres)
pwd
ls -la /var/lib/postgresql/data
exit
```

### 4. CRUD com SELECT no banco após cada operação

Após **CADA** operação no front-end (criar, editar, deletar), abra o terminal do banco e rode:

```bash
docker container exec -it db-dimdim-557481 psql -U dimdim -d dimdimdb
```

Dentro do psql:
```sql
\dt                          -- lista as tabelas
SELECT * FROM clientes;      -- mostra todos os registros
\q                           -- sai do psql
```

### 5. Demonstrar a persistência

```bash
docker container stop db-dimdim-557481
docker container rm db-dimdim-557481

# Recria SEM apagar o volume:
docker container run -d \
  --name db-dimdim-557481 \
  --network dimdim-net-557481 \
  -v dimdim-data-557481:/var/lib/postgresql/data \
  -e POSTGRES_DB=dimdimdb \
  -e POSTGRES_USER=dimdim \
  -e POSTGRES_PASSWORD=dimdim123 \
  -p 5432:5432 \
  postgres:16

# Os dados continuam lá:
docker container exec -it db-dimdim-557481 \
  psql -U dimdim -d dimdimdb -c "SELECT * FROM clientes;"
```

---

## ✅ Checklist de requisitos atendidos

- [x] Dois containers (app + banco)
- [x] Volume nomeado (`dimdim-data-557481`)
- [x] Rede Docker própria (`dimdim-net-557481`)
- [x] CRUD completo em uma tabela (`clientes`)
- [x] Dockerfile com imagem personalizada (`dimdimapp-557481:1.0`)
- [x] Usuário não-root no container da app (`dimdimuser`)
- [x] Diretório de trabalho definido (`/dimdim`)
- [x] Variáveis de ambiente (`DB_HOST`, `DB_USER`, `APP_PORT`, etc.)
- [x] Containers com RM no nome (`app-dimdim-557481`, `db-dimdim-557481`)
- [x] Execução em background (`-d`)
- [x] Hospedagem em nuvem (Azure VM)
- [x] Sem Docker Compose (somente `docker build` + `docker run`)

---

## 🧹 Limpeza do ambiente

Para remover tudo ao final:

```bash
docker container stop app-dimdim-557481 db-dimdim-557481
docker container rm   app-dimdim-557481 db-dimdim-557481
docker network rm     dimdim-net-557481
docker volume rm      dimdim-data-557481
docker image rm       dimdimapp-557481:1.0
```

E no Azure: **Resource Group** → **Delete** (apaga tudo de uma vez).

---

## 📂 Estrutura do repositório

```
dimdimapp/
├── Dockerfile                # Imagem personalizada da aplicação
├── .dockerignore
├── .gitignore
├── README.md                 # Este arquivo
├── run.sh                    # Script atalho com todos os comandos
└── app/
    ├── app.py                # Aplicação Flask
    ├── requirements.txt      # Dependências Python
    └── templates/
        ├── base.html
        ├── index.html        # Listagem
        └── form.html         # Formulário create/update
```

---

## 📚 Referências

- DOCKER INC. Dockerfile reference. Disponível em: https://docs.docker.com/engine/reference/builder/. Acesso em: 18 maio 2026.
- DOCKER INC. Best practices for writing Dockerfiles. Disponível em: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/. Acesso em: 18 maio 2026.
- PALLETS PROJECTS. Flask Documentation. Disponível em: https://flask.palletsprojects.com/. Acesso em: 18 maio 2026.
- POSTGRESQL GLOBAL DEVELOPMENT GROUP. PostgreSQL Documentation. Disponível em: https://www.postgresql.org/docs/. Acesso em: 18 maio 2026.
- MICROSOFT. Azure Virtual Machines documentation. Disponível em: https://learn.microsoft.com/azure/virtual-machines/. Acesso em: 18 maio 2026.
