from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(256), nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    enderecos = db.relationship("Endereco", backref="cliente", cascade="all, delete-orphan")
    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def conferir_senha(self, senha):
        return check_password_hash(self.senha_hash or "", senha)
    
    @property
    def iniciais(self):
        partes = self.nome.split()
        primeira = partes[0][0]
        ultima = partes[-1][0] if len(partes) > 1 else ""
        return (primeira + ultima).upper()

class Endereco(db.Model):
    __tablename__ = "enderecos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    rua = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False, default="Araguaína")
    cep = db.Column(db.String(8))


class Maquiadora(db.Model):
    __tablename__ = "maquiadoras"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)

class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False, unique=True)
    icone = db.Column(db.String(40), nullable=False)

    servicos = db.relationship("Servico", backref="categoria", order_by="Servico.id")


class Servico(db.Model):
    __tablename__ = "servicos"
    __table_args__ = (
        db.CheckConstraint("preco > 0", name="ck_servicos_preco_positivo"),
        db.CheckConstraint("duracao_minutos > 0", name="ck_servicos_duracao_positiva"),
    )

    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(8, 2), nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=False, default="")
    imagem = db.Column(db.String(200), nullable=False)

    itens = db.relationship("ItemServico", backref="servico", cascade="all, delete-orphan", order_by="ItemServico.id")


class ItemServico(db.Model):
    __tablename__ = "itens_servico"

    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id", ondelete="CASCADE"), nullable=False)
    descricao = db.Column(db.String(150), nullable=False)

class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        db.CheckConstraint("nota BETWEEN 1 AND 5", name="ck_avaliacoes_nota_1_a_5"),
    )

    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id", ondelete="CASCADE"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)

    servico = db.relationship("Servico", backref=db.backref("avaliacoes", cascade="all, delete-orphan"))
    cliente = db.relationship("Cliente", backref=db.backref("avaliacoes", cascade="all, delete-orphan"))

class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    __table_args__ = (
        db.UniqueConstraint("maquiadora_id", "data", "horario", name="uq_agendamentos_maquiadora_horario"),
        db.UniqueConstraint("cliente_id", "data", "horario", name="uq_agendamentos_cliente_horario"),
        db.CheckConstraint("forma_pagamento IN ('Pix', 'Cartao')", name="ck_agendamentos_pagamento"),
        db.CheckConstraint("status IN ('confirmado', 'remarcado')", name="ck_agendamentos_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False)
    maquiadora_id = db.Column(db.Integer, db.ForeignKey("maquiadoras.id"), nullable=False)
    endereco_id = db.Column(db.Integer, db.ForeignKey("enderecos.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    forma_pagamento = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(12), nullable=False, default="confirmado")
    criado_em = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    cliente = db.relationship("Cliente", backref=db.backref("agendamentos", cascade="all, delete-orphan"))
    servico = db.relationship("Servico")
    maquiadora = db.relationship("Maquiadora")
    endereco = db.relationship("Endereco")

