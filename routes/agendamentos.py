from datetime import date, time

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from models import Agendamento, Endereco, Servico, db
from regras import HORARIOS, data_valida, endereco_principal, horarios_do_dia, maquiadora_livre
from routes.auth import cliente_logada, login_obrigatorio

bp = Blueprint("agendamentos", __name__, url_prefix="/api")


def ler_data(texto):
    try:
        return date.fromisoformat(texto or "")
    except ValueError:
        return None


def agendamento_json(ag):
    end = ag.endereco
    return {
        "id": ag.id,
        "servico": ag.servico.nome,
        "preco": float(ag.servico.preco),
        "data": ag.data.isoformat(),
        "horario": ag.horario.strftime("%H:%M"),
        "forma_pagamento": ag.forma_pagamento,
        "status": ag.status,
        "maquiadora": ag.maquiadora.nome,
        "endereco": f"{end.rua}, {end.numero} · {end.bairro}, {end.cidade}",
    }

@bp.get("/horarios")
@login_obrigatorio
def horarios():
    dia = ler_data(request.args.get("data"))
    if dia is None or not data_valida(dia):
        return jsonify(erro="Data inválida."), 400
    ignorar = request.args.get("ignorar", type=int)
    return jsonify(horarios_do_dia(dia, cliente_logada().id, ignorar))


@bp.get("/agendamentos")
@login_obrigatorio
def listar():
    lista = (Agendamento.query.filter_by(cliente_id=cliente_logada().id)
             .order_by(Agendamento.data, Agendamento.horario).all())
    return jsonify([agendamento_json(ag) for ag in lista])

@bp.post("/agendamentos")
@login_obrigatorio
def criar():
    cliente = cliente_logada()
    dados = request.get_json(silent=True) or {}

    servico = db.session.get(Servico, dados.get("servico_id") or 0)
    dia = ler_data(dados.get("data"))
    texto_horario = dados.get("horario")
    pagamento = dados.get("forma_pagamento")

    if servico is None:
        return jsonify(erro="Serviço não encontrado."), 400
    if dia is None or not data_valida(dia):
        return jsonify(erro="Escolha uma data válida."), 400
    if texto_horario not in HORARIOS:
        return jsonify(erro="Escolha um horário da lista."), 400
    if pagamento not in ("Pix", "Cartao"):
        return jsonify(erro="Escolha Pix ou Cartão."), 400

    novo = dados.get("endereco")
    if novo:
        rua = (novo.get("rua") or "").strip()
        numero = (novo.get("numero") or "").strip()
        bairro = (novo.get("bairro") or "").strip()
        if not rua or not numero or not bairro or len(numero) > 10:
            return jsonify(erro="Preencha rua, número e bairro."), 400
        endereco = Endereco(cliente_id=cliente.id, rua=rua, numero=numero,
                            bairro=bairro, cidade="Araguaína")
    else:
        endereco = endereco_principal(cliente.id)
    if endereco is None:
        return jsonify(erro="Informe o endereço do atendimento."), 400

    livres = [h["horario"] for h in horarios_do_dia(dia, cliente.id) if h["disponivel"]]
    if texto_horario not in livres:
        return jsonify(erro="Esse horário não está disponível. Escolha outro."), 409

    horario = time.fromisoformat(texto_horario)
    agendamento = Agendamento(cliente_id=cliente.id, servico_id=servico.id,
                              maquiadora_id=maquiadora_livre(dia, horario).id,
                              endereco=endereco, data=dia, horario=horario,
                              forma_pagamento=pagamento)
    db.session.add(agendamento)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(erro="Esse horário acabou de ser ocupado. Escolha outro."), 409
    return jsonify(agendamento_json(agendamento)), 201

