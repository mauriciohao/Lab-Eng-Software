from models import banco

class Despesa(banco.Model):
    __tablename__ = 'despesa'

    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(100), nullable=False)
    descricao = banco.Column(banco.Text)
    estabelecimento = banco.Column(banco.String(100))
    categoria = banco.Column(banco.String(50))
    valor = banco.Column(banco.Float, nullable=False)
    data = banco.Column(banco.Date, nullable=False)
    data_limite = banco.Column(banco.Date)
    metodo_divisao = banco.Column(banco.String(20), nullable=False)
    status = banco.Column(banco.String(20), nullable=False, default='pendente')

    grupo_id = banco.Column(banco.Integer, banco.ForeignKey('grupo.id'), nullable=False)
    pagador_id = banco.Column(banco.Integer, banco.ForeignKey('usuario.id'), nullable=False)

    pagador = banco.relationship('Usuario', backref='despesas_pagadoras')
    divisoes = banco.relationship('Divisao', backref='despesa', lazy=True)

    def __repr__(self):
        return f'<Despesa {self.nome} - R${self.valor}>'
