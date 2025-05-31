from models import banco

grupo_usuario = banco.Table('grupo_usuario',
    banco.Column('usuario_id', banco.Integer, banco.ForeignKey('usuario.id')),
    banco.Column('grupo_id', banco.Integer, banco.ForeignKey('grupo.id'))
)

class Usuario(banco.Model):
    __tablename__ = 'usuario'

    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(100), nullable=False)
    email = banco.Column(banco.String(100), nullable=False, unique=True)
    username = banco.Column(banco.String(50), nullable=False, unique=True)
    senha = banco.Column(banco.String(100), nullable=False)

    grupos = banco.relationship('Grupo', secondary=grupo_usuario, back_populates='membros')

    def __repr__(self):
        return f'<Usuario {self.nome}>'
