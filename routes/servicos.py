from flask import Blueprint, jsonify, request
from sqlalchemy import func

from models import Avaliacao, Categoria, Servico, db

bp = Blueprint("servicos", __name__, url_prefix="/api")


def servico_resumo(servico):
    return {
        "id": servico.id,
        "nome": servico.nome,
        "preco": float(servico.preco),
        "duracao_minutos": servico.duracao_minutos,
        "imagem": servico.imagem,
        "categoria_id": servico.categoria_id,
    }
def media_avaliacoes(servico_id):
    media, total = (db.session.query(func.avg(Avaliacao.nota), func.count(Avaliacao.id))
                    .filter(Avaliacao.servico_id == servico_id).one())
    return (round(float(media), 1) if media else None), total


@bp.get("/categorias")
def listar_categorias():
    categorias = Categoria.query.order_by(Categoria.id).all()
    return jsonify([{"id": c.id, "nome": c.nome, "icone": c.icone} for c in categorias])


@bp.get("/categorias/<int:categoria_id>/servicos")
def servicos_da_categoria(categoria_id):
    categoria = db.get_or_404(Categoria, categoria_id)
    return jsonify([servico_resumo(s) for s in categoria.servicos])


@bp.get("/servicos")
def buscar_servicos():
    busca = request.args.get("busca", "").strip()
    consulta = Servico.query.order_by(Servico.id)
    if busca:
        consulta = consulta.filter(Servico.nome.ilike(f"%{busca}%"))
    return jsonify([servico_resumo(s) for s in consulta.all()])


@bp.get("/servicos/<int:servico_id>")
def detalhes_servico(servico_id):
    servico = db.get_or_404(Servico, servico_id)
    media, total = media_avaliacoes(servico.id)
    dados = servico_resumo(servico)
    dados["descricao"] = servico.descricao
    dados["itens"] = [item.descricao for item in servico.itens]
    dados["avaliacao_media"] = media
    dados["total_avaliacoes"] = total
    return jsonify(dados)