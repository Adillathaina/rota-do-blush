import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import text

from models import db

PASTA_DO_PROJETO = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(PASTA_DO_PROJETO, ".env"))

migrate = Migrate()

def endereco_do_banco():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return "sqlite:///" + os.path.join(PASTA_DO_PROJETO, "rota_do_blush.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def create_app(config=None):
    app = Flask(__name__)

    em_producao = "RENDER" in os.environ
    chave = os.environ.get("SECRET_KEY")
    if em_producao and not chave:
        raise RuntimeError("Defina a variável SECRET_KEY no Render.")

    app.config["SECRET_KEY"] = chave or "chave-so-para-desenvolvimento"
    app.config["SQLALCHEMY_DATABASE_URI"] = endereco_do_banco()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = em_producao

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def inicio():
        return "Olá, Rota do Blush!"

    @app.route("/teste-banco")
    def teste_banco():
        db.session.execute(text("SELECT 1"))
        return "Banco conectado: " + db.engine.dialect.name

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)