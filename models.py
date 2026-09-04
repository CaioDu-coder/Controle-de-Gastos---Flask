from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Gasto(db.Model):
    """Representa um gasto/despesa cadastrado pelo usuário."""

    __tablename__ = "gastos"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(150), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Gasto {self.descricao} - R$ {self.valor:.2f}>"
