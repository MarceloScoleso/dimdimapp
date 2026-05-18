# ============================================================================
# Dockerfile - DimDimApp (Aplicação Flask MVC)
# ============================================================================
# CP3 - DevOps Tools and Cloud Computing
# Marcelo Antônio Scoleso Júnior - RM 557481 (representante)
# João Paulo Francisco de Oliveira - RM 557410
# ============================================================================

# Imagem base oficial Python - versão slim para imagem menor
FROM python:3.11-slim

# ----------------------------------------------------------------------------
# METADADOS DA IMAGEM
# ----------------------------------------------------------------------------
LABEL maintainer="Marcelo A. S. Junior - RM 557481"
LABEL description="Aplicação Flask MVC para gestão de clientes - DimDimApp"
LABEL version="1.0"

# ----------------------------------------------------------------------------
# VARIÁVEIS DE AMBIENTE (REQUISITO: pelo menos uma variável de ambiente)
# ----------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/dimdim \
    APP_USER=dimdimuser \
    APP_PORT=5000

# ----------------------------------------------------------------------------
# DIRETÓRIO DE TRABALHO (REQUISITO: definir diretório de trabalho)
# ----------------------------------------------------------------------------
WORKDIR ${APP_HOME}

# ----------------------------------------------------------------------------
# DEPENDÊNCIAS DO SISTEMA
# ----------------------------------------------------------------------------
# Instala dependências do sistema necessárias para psycopg2 e remove cache
# para manter a imagem enxuta
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------------
# DEPENDÊNCIAS PYTHON
# ----------------------------------------------------------------------------
# Copia primeiro o requirements para aproveitar o cache do Docker
COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------------------------
# CÓDIGO DA APLICAÇÃO
# ----------------------------------------------------------------------------
COPY app/ ${APP_HOME}/

# ----------------------------------------------------------------------------
# USUÁRIO NÃO-ROOT (REQUISITO OBRIGATÓRIO - menos 2 pontos se rodar como root)
# ----------------------------------------------------------------------------
# Cria um grupo e usuário dedicado, define como dono dos arquivos da aplicação
RUN groupadd -r ${APP_USER} && \
    useradd -r -g ${APP_USER} -d ${APP_HOME} -s /bin/bash ${APP_USER} && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Troca para o usuário não-root (todas as instruções daqui pra frente rodam como ele)
USER ${APP_USER}

# ----------------------------------------------------------------------------
# PORTA E HEALTHCHECK
# ----------------------------------------------------------------------------
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# ----------------------------------------------------------------------------
# COMANDO DE INICIALIZAÇÃO
# ----------------------------------------------------------------------------
# Usa gunicorn em produção (mais robusto que o servidor de desenvolvimento Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", \
     "--access-logfile", "-", "--error-logfile", "-", "app:app"]
