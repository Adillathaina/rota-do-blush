import re
from functools import wraps

from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for

from models import Cliente, db

bp = Blueprint("auth", __name__)

EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def cliente_logada():
    cliente_id = session.get("cliente_id")
    if cliente_id is None:
        return None
    cliente = g.get("cliente")
    if cliente is None or cliente.id != cliente_id:
        cliente = db.session.get(Cliente, cliente_id)
        g.cliente = cliente
    return cliente


def login_obrigatorio(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if cliente_logada() is None:
            if request.path.startswith("/api/"):
                return jsonify(erro="Faça login para continuar."), 401
            return redirect(url_for("auth.login", proxima=request.full_path.rstrip("?")))
        return funcao(*args, **kwargs)
    return protegida

@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html", dados={})

    dados = request.form
    nome = dados.get("nome", "").strip()
    telefone = re.sub(r"\D", "", dados.get("telefone", ""))
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    erros = []
    if len(nome) < 3:
        erros.append("Informe seu nome (pelo menos 3 letras).")
    if len(telefone) not in (10, 11):
        erros.append("Informe o telefone com DDD.")
    if not EMAIL_VALIDO.match(email):
        erros.append("Informe um email válido.")
    if len(senha) < 6:
        erros.append("A senha precisa ter pelo menos 6 caracteres.")
    if not erros and Cliente.query.filter_by(email=email).first():
        erros.append("Este email já está cadastrado.")

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("cadastro.html", dados=dados), 400

    cliente = Cliente(nome=nome, telefone=telefone, email=email)
    cliente.definir_senha(senha)
    db.session.add(cliente)
    db.session.commit()

    session.clear()
    session["cliente_id"] = cliente.id
    flash("Conta criada! Bem-vinda à Rota do Blush.", "sucesso")
    return redirect(url_for("paginas.home"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    proxima = request.args.get("proxima", "")
    if request.method == "GET":
        return render_template("login.html", proxima=proxima)

    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    cliente = Cliente.query.filter_by(email=email).first()

    if cliente is None or not cliente.conferir_senha(senha):
        flash("Email ou senha incorretos.", "erro")
        return render_template("login.html", proxima=proxima, email=email), 401

    session.clear()
    session["cliente_id"] = cliente.id
    if not proxima.startswith("/") or proxima.startswith("//"):
        proxima = url_for("paginas.home")
    return redirect(proxima)


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

