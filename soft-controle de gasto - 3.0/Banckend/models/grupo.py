from models import banco
from models.usuario import grupo_usuario  # Importa a tabela de associação

class Grupo(banco.Model):
    __tablename__ = 'grupo'

    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(100), nullable=False)
    descricao = banco.Column(banco.Text)
    regras = banco.Column(banco.Text)
    codigo_convite = banco.Column(banco.String(10), nullable=False, unique=True)

    membros = banco.relationship('Usuario', secondary=grupo_usuario, back_populates='grupos')
    despesas = banco.relationship('Despesa', backref='grupo', lazy=True)

    def __repr__(self):
        return f'<Grupo {self.nome}>'
