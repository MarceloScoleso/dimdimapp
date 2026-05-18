"""
============================================================================
DimDimApp - Sistema de Gestão de Clientes
============================================================================
Aplicação Flask MVC com CRUD completo conectada ao PostgreSQL.
Projeto Checkpoint 3 - DevOps Tools and Cloud Computing

Integrantes:
    - Marcelo Antônio Scoleso Júnior - RM 557481 (representante)
    - João Paulo Francisco de Oliveira - RM 557410
============================================================================
"""

import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor

# ============================================================================
# CONFIGURAÇÃO - VARIÁVEIS DE AMBIENTE
# ============================================================================
# As variáveis abaixo são carregadas do ambiente do container (definidas
# no docker run via -e ou no Dockerfile via ENV)

DB_HOST = os.environ.get("DB_HOST", "db-dimdim-557481")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "dimdimdb")
DB_USER = os.environ.get("DB_USER", "dimdim")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "dimdim123")
APP_PORT = int(os.environ.get("APP_PORT", "5000"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dimdim-secret-key-557481")


# ============================================================================
# CONEXÃO COM O BANCO
# ============================================================================

def get_db_connection():
    """Cria e retorna uma conexão com o PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    """Inicializa a tabela 'clientes' se ela ainda não existir.
    Faz tentativas com retry, pois o container do banco pode levar
    alguns segundos para subir."""
    tentativas = 15
    for i in range(tentativas):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id          SERIAL PRIMARY KEY,
                    nome        VARCHAR(100) NOT NULL,
                    cpf         VARCHAR(14)  NOT NULL UNIQUE,
                    email       VARCHAR(100) NOT NULL,
                    saldo       NUMERIC(12,2) DEFAULT 0.00,
                    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print(f"[init_db] Tabela 'clientes' pronta (tentativa {i+1}).")
            return
        except Exception as e:
            print(f"[init_db] Tentativa {i+1}/{tentativas} falhou: {e}")
            time.sleep(3)
    raise RuntimeError("Não foi possível inicializar o banco após várias tentativas.")


# ============================================================================
# ROTAS - CRUD
# ============================================================================

@app.route("/")
def index():
    """READ - Lista todos os clientes."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes ORDER BY id ASC;")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", clientes=clientes)


@app.route("/novo", methods=["GET", "POST"])
def novo_cliente():
    """CREATE - Cadastra um novo cliente."""
    if request.method == "POST":
        nome = request.form["nome"].strip()
        cpf = request.form["cpf"].strip()
        email = request.form["email"].strip()
        saldo = request.form.get("saldo", "0").strip() or "0"

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO clientes (nome, cpf, email, saldo) "
                "VALUES (%s, %s, %s, %s);",
                (nome, cpf, email, float(saldo)),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash(f"Cliente '{nome}' cadastrado com sucesso!", "success")
            return redirect(url_for("index"))
        except psycopg2.errors.UniqueViolation:
            flash("Erro: já existe um cliente com este CPF.", "error")
        except Exception as e:
            flash(f"Erro ao cadastrar cliente: {e}", "error")

    return render_template("form.html", cliente=None, acao="Novo")


@app.route("/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    """UPDATE - Edita os dados de um cliente."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        nome = request.form["nome"].strip()
        cpf = request.form["cpf"].strip()
        email = request.form["email"].strip()
        saldo = request.form.get("saldo", "0").strip() or "0"

        try:
            cur.execute(
                "UPDATE clientes SET nome=%s, cpf=%s, email=%s, saldo=%s "
                "WHERE id=%s;",
                (nome, cpf, email, float(saldo), cliente_id),
            )
            conn.commit()
            flash(f"Cliente '{nome}' atualizado com sucesso!", "success")
            cur.close()
            conn.close()
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao atualizar cliente: {e}", "error")

    cur.execute("SELECT * FROM clientes WHERE id=%s;", (cliente_id,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()

    if not cliente:
        flash("Cliente não encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("form.html", cliente=cliente, acao="Editar")


@app.route("/deletar/<int:cliente_id>", methods=["POST"])
def deletar_cliente(cliente_id):
    """DELETE - Remove um cliente."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM clientes WHERE id=%s;", (cliente_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash(f"Cliente ID {cliente_id} removido com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao remover cliente: {e}", "error")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    """Endpoint de health check."""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "db": "connected"}, 200
    except Exception as e:
        return {"status": "error", "db": str(e)}, 500


# ============================================================================
# INICIALIZAÇÃO (roda tanto via gunicorn quanto via "python app.py")
# ============================================================================
print("=" * 60)
print(" DimDimApp - Sistema de Gestão de Clientes")
print(" RM 557481 - Marcelo Antônio Scoleso Júnior")
print(" RM 557410 - João Paulo Francisco de Oliveira")
print("=" * 60)
print(f" DB_HOST: {DB_HOST}")
print(f" DB_NAME: {DB_NAME}")
print(f" APP_PORT: {APP_PORT}")
print("=" * 60)

init_db()


# ============================================================================
# MAIN - só executa quando rodado via "python app.py" (modo desenvolvimento)
# ============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT, debug=False)
