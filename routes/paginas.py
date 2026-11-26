from flask import Blueprint, render_template

from models import Categoria, db
from routes.auth import login_obrigatorio

bp = Blueprint("paginas", __name__)


@bp.get("/")
@login_obrigatorio
def home():
    categorias = Categoria.query.order_by(Categoria.id).all()
    return render_template("home.html", categorias=categorias, aba="inicio")


@bp.get("/categoria/<int:categoria_id>")
@login_obrigatorio
def listagem(categoria_id):
    categoria = db.get_or_404(Categoria, categoria_id)
    return render_template("listagem.html", titulo=categoria.nome,
                           servicos=categoria.servicos, aba="inicio")

@bp.app_template_filter("duracao")
def formatar_duracao(minutos):
    horas, resto = divmod(minutos, 60)
    if horas == 0:
        return f"{resto}min"
    if resto == 0:
        return f"{horas}h"
    return f"{horas}h{resto:02d}"