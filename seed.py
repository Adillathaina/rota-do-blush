import sys

from models import (Avaliacao, Agendamento, Categoria, Cliente, Endereco,
                    ItemServico, Maquiadora, Servico, db)

CATEGORIAS = [
    ("Maquiagem Social", "brilho"),
    ("Noivas", "aliancas"),
    ("Artística", "pincel"),
    ("Formaturas", "capelo"),
]

SERVICOS = [
    ("Maquiagem Social", "Make Glam", 180, 90, "make-glam.jpg",
     "Maquiagem marcante com pele iluminada e olhos esfumados, ideal para festas e eventos à noite.",
     ["Preparação e skincare da pele", "Maquiagem completa com acabamento glam",
      "Cílios postiços", "Fixação para longa duração"]),
    ("Maquiagem Social", "Make Natural", 120, 60, "make-natural.jpg",
     "Maquiagem leve que realça a beleza natural, perfeita para o dia a dia e eventos durante o dia.",
     ["Preparação e skincare da pele", "Pele leve com acabamento natural",
      "Máscara de cílios e sobrancelhas", "Fixação para longa duração"]),
    ("Maquiagem Social", "Make Soft Glow", 140, 75, "make-soft-glow.jpg",
     "Pele radiante com brilho suave e tons pêssego, para um visual iluminado e delicado.",
     ["Preparação e skincare da pele", "Pele iluminada com efeito glow",
      "Sombras em tons quentes e suaves", "Fixação para longa duração"]),
    ("Maquiagem Social", "Make Festa", 200, 105, "make-festa.jpg",
     "Produção completa para festas, com olhos marcantes e batom de destaque.",
     ["Preparação e skincare da pele", "Maquiagem completa para festa",
      "Cílios postiços", "Fixação à prova de suor"]),
    ("Noivas", "Make Noiva Clássica", 450, 150, "make-noiva-classica.jpg",
     "Maquiagem de noiva elegante e atemporal, feita para durar da cerimônia ao fim da festa.",
     ["Preparação e skincare da pele", "Maquiagem completa de noiva",
      "Cílios postiços fio a fio", "Fixação para longa duração", "Kit de retoque para a festa"]),
    ("Noivas", "Teste de Make Noiva", 200, 90, "teste-make-noiva.jpg",
     "Ensaio da maquiagem do grande dia, para definir o visual com calma antes do casamento.",
     ["Conversa sobre o estilo desejado", "Maquiagem completa de teste",
      "Ajustes até chegar ao visual ideal", "Fotos de referência para o dia"]),
    ("Artística", "Make Artística", 220, 120, "make-artistica.jpg",
     "Maquiagem criativa com cores e traços gráficos, para ensaios, editoriais e eventos temáticos.",
     ["Preparação da pele", "Criação artística personalizada",
      "Delineados e sombras coloridas", "Fixação para longa duração"]),
    ("Artística", "Make Fantasia", 160, 90, "make-fantasia.jpg",
     "Maquiagem divertida com glitter e pedrarias, perfeita para Carnaval, Halloween e festas à fantasia.",
     ["Preparação da pele", "Maquiagem temática",
      "Aplicação de glitter e pedrarias", "Fixação resistente ao calor"]),
    ("Formaturas", "Make Formatura", 200, 105, "make-formatura.jpg",
     "Maquiagem sofisticada para a colação e o baile, com acabamento que fica lindo nas fotos.",
     ["Preparação e skincare da pele", "Maquiagem completa para formatura",
      "Cílios postiços", "Fixação para longa duração"]),
    ("Formaturas", "Make Formanda + Mãe", 340, 165, "make-formanda-mae.jpg",
     "Maquiagem para a formanda e para a mãe no mesmo atendimento, para as duas brilharem juntas.",
     ["Preparação da pele das duas", "Maquiagem completa para a formanda",
      "Maquiagem completa para a mãe", "Cílios postiços para as duas"]),
]

MAQUIADORAS = [
    ("Camila Rocha", "63999990001"),
    ("Juliana Alves", "63999990002"),
]

CLIENTES_EXEMPLO = [
    ("Ana Souza", "63999990011", "teste1@rotadoblush.com"),
    ("Beatriz Lima", "63999990012", "teste2@rotadoblush.com"),
    ("Carla Mendes", "63999990013", "teste3@rotadoblush.com"),
]

AVALIACOES = {
    "Make Glam": (116, 12),
    "Make Natural": (40, 5),
    "Make Soft Glow": (30, 6),
    "Make Festa": (52, 8),
    "Make Noiva Clássica": (64, 2),
    "Teste de Make Noiva": (25, 3),
    "Make Artística": (18, 4),
    "Make Fantasia": (22, 5),
    "Make Formatura": (35, 4),
    "Make Formanda + Mãe": (14, 1),
}

def limpar():
    for modelo in (Agendamento, Avaliacao, ItemServico, Servico, Categoria,
                   Endereco, Cliente, Maquiadora):
        db.session.query(modelo).delete()
    db.session.commit()
    print("Dados antigos apagados.")


def popular():
    if Categoria.query.first():
        print("O banco já tem dados. Use: python seed.py --reset")
        return

    categorias = {}
    for nome, icone in CATEGORIAS:
        categoria = Categoria(nome=nome, icone=icone)
        db.session.add(categoria)
        categorias[nome] = categoria

    servicos = {}
    for nome_categoria, nome, preco, duracao, foto, descricao, itens in SERVICOS:
        servico = Servico(categoria=categorias[nome_categoria], nome=nome, preco=preco,
                          duracao_minutos=duracao, descricao=descricao,
                          imagem="img/servicos/" + foto)
        for texto in itens:
            servico.itens.append(ItemServico(descricao=texto))
        db.session.add(servico)
        servicos[nome] = servico

    for nome, telefone in MAQUIADORAS:
        db.session.add(Maquiadora(nome=nome, telefone=telefone))

    clientes = []
    for nome, telefone, email in CLIENTES_EXEMPLO:
        cliente = Cliente(nome=nome, telefone=telefone, email=email)
        db.session.add(cliente)
        clientes.append(cliente)

    for nome_servico, (notas_5, notas_4) in AVALIACOES.items():
        notas = [5] * notas_5 + [4] * notas_4
        for posicao, nota in enumerate(notas):
            autora = clientes[posicao % len(clientes)]
            db.session.add(Avaliacao(servico=servicos[nome_servico], cliente=autora, nota=nota))

    db.session.commit()
    print("Banco populado com sucesso!")


if __name__ == "__main__":
    from app import app

    with app.app_context():
        if "--reset" in sys.argv:
            limpar()
        popular()