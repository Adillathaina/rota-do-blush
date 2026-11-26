from datetime import datetime, time, timedelta, timezone

from models import Agendamento, Endereco, Maquiadora

FUSO_ARAGUAINA = timezone(timedelta(hours=-3))
HORARIOS = ["08:00", "09:30", "11:00", "14:00", "15:30", "17:00", "18:30", "19:30"]
DIAS_DE_ANTECEDENCIA = 90


def agora():
    return datetime.now(FUSO_ARAGUAINA).replace(tzinfo=None)


def data_valida(dia):
    hoje = agora().date()
    return hoje <= dia <= hoje + timedelta(days=DIAS_DE_ANTECEDENCIA)


def endereco_principal(cliente_id):
    return (Endereco.query.filter_by(cliente_id=cliente_id)
            .order_by(Endereco.id.desc()).first())


def maquiadora_livre(dia, horario, ignorar=None):
    consulta = Agendamento.query.filter_by(data=dia, horario=horario)
    if ignorar:
        consulta = consulta.filter(Agendamento.id != ignorar)
    ocupadas = [ag.maquiadora_id for ag in consulta]
    return (Maquiadora.query.filter(Maquiadora.id.not_in(ocupadas))
            .order_by(Maquiadora.id).first())


def cliente_ocupada(cliente_id, dia, horario, ignorar=None):
    consulta = Agendamento.query.filter_by(cliente_id=cliente_id, data=dia, horario=horario)
    if ignorar:
        consulta = consulta.filter(Agendamento.id != ignorar)
    return consulta.first() is not None


def horarios_do_dia(dia, cliente_id, ignorar=None):
    momento = agora()
    lista = []
    for texto in HORARIOS:
        horario = time.fromisoformat(texto)
        ja_passou = datetime.combine(dia, horario) <= momento
        disponivel = (not ja_passou
                      and maquiadora_livre(dia, horario, ignorar) is not None
                      and not cliente_ocupada(cliente_id, dia, horario, ignorar))
        lista.append({"horario": texto, "disponivel": disponivel})
    return lista