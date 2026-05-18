#!/bin/bash
# ============================================================================
# Script de subida do ambiente DimDimApp
# CP3 - DevOps - RM 557481
# ============================================================================
# Atalho que executa todos os comandos do README na ordem certa.
# Use para subir o ambiente sem precisar digitar comando por comando.
# (No vídeo, recomendamos digitar os comandos manualmente para ficar didático.)
# ============================================================================

set -e

RM="557481"
NETWORK="dimdim-net-${RM}"
VOLUME="dimdim-data-${RM}"
DB_CONTAINER="db-dimdim-${RM}"
APP_CONTAINER="app-dimdim-${RM}"
IMAGE="dimdimapp-${RM}:1.0"

echo "============================================================"
echo "  DimDimApp - Subida do ambiente Docker"
echo "  Representante: Marcelo A. S. Junior - RM ${RM}"
echo "============================================================"

echo ""
echo "[1/6] Criando rede Docker..."
docker network create ${NETWORK} 2>/dev/null || echo "  -> rede já existe"

echo ""
echo "[2/6] Criando volume nomeado..."
docker volume create ${VOLUME} 2>/dev/null || echo "  -> volume já existe"

echo ""
echo "[3/6] Construindo a imagem da aplicação..."
docker build -t ${IMAGE} .

echo ""
echo "[4/6] Subindo container do banco (PostgreSQL)..."
docker container rm -f ${DB_CONTAINER} 2>/dev/null || true
docker container run -d \
  --name ${DB_CONTAINER} \
  --network ${NETWORK} \
  -v ${VOLUME}:/var/lib/postgresql/data \
  -e POSTGRES_DB=dimdimdb \
  -e POSTGRES_USER=dimdim \
  -e POSTGRES_PASSWORD=dimdim123 \
  -p 5432:5432 \
  postgres:16

echo ""
echo "[5/6] Aguardando o banco subir (15s)..."
sleep 15

echo ""
echo "[6/6] Subindo container da aplicação..."
docker container rm -f ${APP_CONTAINER} 2>/dev/null || true
docker container run -d \
  --name ${APP_CONTAINER} \
  --network ${NETWORK} \
  -e DB_HOST=${DB_CONTAINER} \
  -e DB_PORT=5432 \
  -e DB_NAME=dimdimdb \
  -e DB_USER=dimdim \
  -e DB_PASSWORD=dimdim123 \
  -p 80:5000 \
  ${IMAGE}

# Descobre o IP público da VM (Azure)
IP=$(curl -s --max-time 3 ifconfig.me 2>/dev/null || echo "<IP_PUBLICO_DA_VM>")

echo ""
echo "============================================================"
echo "  ✅ Ambiente pronto!"
echo "============================================================"
echo "  Acesse:  http://${IP}"
echo ""
echo "  Containers ativos:"
docker container ls --filter "name=dimdim"
echo "============================================================"
