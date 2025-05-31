from models import banco

class Divisao(banco.Model):
    __tablename__ = 'divisao'

    id = banco.Column(banco.Integer, primary_key=True)
    despesa_id = banco.Column(banco.Integer, banco.ForeignKey('despesa.id'), nullable=False)
    usuario_id = banco.Column(banco.Integer, banco.ForeignKey('usuario.id'), nullable=False)
    valor = banco.Column(banco.Float, nullable=False)

    usuario = banco.relationship('Usuario', backref='divisoes')

    def __repr__(self):
        return f'<Divisão: Usuario {self.usuario_id} deve R$ {self.valor:.2f} na despesa {self.despesa_id}>'
