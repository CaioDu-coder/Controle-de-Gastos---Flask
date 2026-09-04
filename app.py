import os
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
)

from models import db, Gasto

# ---------------------------------------------------------------------------
# Configuração da aplicação
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-secreta-controle-de-gastos-2026"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "gastos.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

CATEGORIAS = ["Alimentação", "Transporte", "Moradia", "Saúde", "Lazer", "Educação", "Outros"]
FORMAS_PAGAMENTO = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Transferência"]

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Contexto global para os templates (cookie de tema, listas de opções, etc.)
# ---------------------------------------------------------------------------
@app.context_processor
def injetar_variaveis_globais():
    tema = request.cookies.get("tema", "claro")  # cookie de preferência do visitante
    return dict(
        categorias=CATEGORIAS,
        formas_pagamento=FORMAS_PAGAMENTO,
        tema_atual=tema,
        ano_atual=datetime.now().year,
    )


def validar_gasto(form):
    """Valida os dados enviados no formulário de gasto. Retorna (erros, dados_limpos)."""
    erros = []

    descricao = form.get("descricao", "").strip()
    valor_bruto = form.get("valor", "").strip()
    categoria = form.get("categoria", "").strip()
    data_str = form.get("data", "").strip()
    forma_pagamento = form.get("forma_pagamento", "").strip()

    if not descricao or len(descricao) < 3:
        erros.append("A descrição deve ter pelo menos 3 caracteres.")

    valor_float = None
    try:
        valor_float = float(valor_bruto.replace(",", "."))
        if valor_float <= 0:
            erros.append("O valor deve ser maior que zero.")
    except (ValueError, AttributeError):
        erros.append("Informe um valor numérico válido para o gasto.")

    if categoria not in CATEGORIAS:
        erros.append("Selecione uma categoria válida.")

    if forma_pagamento not in FORMAS_PAGAMENTO:
        erros.append("Selecione uma forma de pagamento válida.")

    data_gasto = None
    try:
        data_gasto = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        erros.append("Informe uma data válida.")

    dados = {
        "descricao": descricao,
        "valor": valor_float,
        "categoria": categoria,
        "data": data_gasto,
        "forma_pagamento": forma_pagamento,
    }
    return erros, dados


# ---------------------------------------------------------------------------
# Rota 1: Dashboard inicial
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    total_gastos = Gasto.query.count()
    soma_total = db.session.query(db.func.sum(Gasto.valor)).scalar() or 0
    ultimos_gastos = Gasto.query.order_by(Gasto.data.desc(), Gasto.id.desc()).limit(5).all()
    return render_template(
        "index.html",
        total_gastos=total_gastos,
        soma_total=soma_total,
        ultimos_gastos=ultimos_gastos,
    )


# ---------------------------------------------------------------------------
# Rota 2: Listagem de gastos (Read - lista) com filtro por categoria via session
# ---------------------------------------------------------------------------
@app.route("/gastos")
def listar_gastos():
    filtro = request.args.get("categoria")
    if filtro:
        session["ultimo_filtro"] = filtro  # guarda preferência na sessão
    else:
        filtro = session.get("ultimo_filtro", "Todas")

    consulta = Gasto.query
    if filtro and filtro != "Todas":
        consulta = consulta.filter_by(categoria=filtro)
    gastos = consulta.order_by(Gasto.data.desc()).all()

    soma_filtrada = sum(g.valor for g in gastos)

    return render_template(
        "listar.html",
        gastos=gastos,
        filtro_atual=filtro or "Todas",
        soma_filtrada=soma_filtrada,
    )


# ---------------------------------------------------------------------------
# Rota 3: Detalhe de um gasto (Read - detalhe) - rota com parâmetro na URL
# ---------------------------------------------------------------------------
@app.route("/resumo")
def resumo():
    total_gastos = Gasto.query.count()
    soma_total = db.session.query(db.func.sum(Gasto.valor)).scalar() or 0
    media_gasto = (soma_total / total_gastos) if total_gastos else 0

    maior_gasto = Gasto.query.order_by(Gasto.valor.desc()).first()

    # Soma agrupada por categoria
    resultado_categorias = (
        db.session.query(Gasto.categoria, db.func.sum(Gasto.valor), db.func.count(Gasto.id))
        .group_by(Gasto.categoria)
        .order_by(db.func.sum(Gasto.valor).desc())
        .all()
    )
    resumo_categorias = [
        {
            "categoria": categoria,
            "total": total,
            "quantidade": quantidade,
            "percentual": (total / soma_total * 100) if soma_total else 0,
        }
        for categoria, total, quantidade in resultado_categorias
    ]

    # Soma agrupada por forma de pagamento
    resultado_formas = (
        db.session.query(Gasto.forma_pagamento, db.func.sum(Gasto.valor), db.func.count(Gasto.id))
        .group_by(Gasto.forma_pagamento)
        .order_by(db.func.sum(Gasto.valor).desc())
        .all()
    )
    resumo_formas = [
        {
            "forma_pagamento": forma,
            "total": total,
            "quantidade": quantidade,
            "percentual": (total / soma_total * 100) if soma_total else 0,
        }
        for forma, total, quantidade in resultado_formas
    ]

    return render_template(
        "resumo.html",
        total_gastos=total_gastos,
        soma_total=soma_total,
        media_gasto=media_gasto,
        maior_gasto=maior_gasto,
        resumo_categorias=resumo_categorias,
        resumo_formas=resumo_formas,
    )


@app.route("/gasto/<int:id>")
def detalhe_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    return render_template("detalhe.html", gasto=gasto)


# ---------------------------------------------------------------------------
# Rota 4: Cadastrar novo gasto (Create) - GET e POST na mesma rota
# ---------------------------------------------------------------------------
@app.route("/gasto/novo", methods=["GET", "POST"])
def novo_gasto():
    if request.method == "POST":
        erros, dados = validar_gasto(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template("form.html", modo="novo", gasto=dict(request.form))

        novo = Gasto(**dados)
        db.session.add(novo)
        db.session.commit()

        # contador temporário de cadastros feitos nesta sessão do navegador
        session["gastos_cadastrados_sessao"] = session.get("gastos_cadastrados_sessao", 0) + 1

        flash(f'Gasto "{dados["descricao"]}" cadastrado com sucesso!', "sucesso")
        return redirect(url_for("listar_gastos"))

    return render_template("form.html", modo="novo", gasto=None, data_hoje=date.today().isoformat())


# ---------------------------------------------------------------------------
# Rota 5: Editar gasto existente (Update) - GET e POST na mesma rota
# ---------------------------------------------------------------------------
@app.route("/gasto/editar/<int:id>", methods=["GET", "POST"])
def editar_gasto(id):
    gasto = Gasto.query.get_or_404(id)

    if request.method == "POST":
        erros, dados = validar_gasto(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            gasto_temp = {"id": id, **dict(request.form)}
            return render_template("form.html", modo="editar", gasto=gasto_temp)

        gasto.descricao = dados["descricao"]
        gasto.valor = dados["valor"]
        gasto.categoria = dados["categoria"]
        gasto.data = dados["data"]
        gasto.forma_pagamento = dados["forma_pagamento"]
        db.session.commit()

        flash(f'Gasto "{gasto.descricao}" atualizado com sucesso!', "sucesso")
        return redirect(url_for("detalhe_gasto", id=id))

    gasto_dict = {
        "id": gasto.id,
        "descricao": gasto.descricao,
        "valor": gasto.valor,
        "categoria": gasto.categoria,
        "data": gasto.data.isoformat(),
        "forma_pagamento": gasto.forma_pagamento,
    }
    return render_template("form.html", modo="editar", gasto=gasto_dict)


# ---------------------------------------------------------------------------
# Rota 6: Remover gasto (Delete)
# ---------------------------------------------------------------------------
@app.route("/gasto/deletar/<int:id>", methods=["POST"])
def deletar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    descricao = gasto.descricao
    db.session.delete(gasto)
    db.session.commit()
    flash(f'Gasto "{descricao}" removido com sucesso!', "sucesso")
    return redirect(url_for("listar_gastos"))


# ---------------------------------------------------------------------------
# Rota 7: Preferência de tema (grava um cookie no navegador do visitante)
# ---------------------------------------------------------------------------
@app.route("/preferencias/tema/<tema>")
def definir_tema(tema):
    if tema not in ("claro", "escuro"):
        tema = "claro"
    destino = request.referrer or url_for("index")
    resposta = make_response(redirect(destino))
    resposta.set_cookie("tema", tema, max_age=60 * 60 * 24 * 365)  # 1 ano
    return resposta


if __name__ == "__main__":
    app.run(debug=True)
