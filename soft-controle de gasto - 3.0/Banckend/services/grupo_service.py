from models.grupo import Grupo
from models.usuario import Usuario
from models import banco

class GrupoService:

    @staticmethod
    def listar_grupos_por_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None
        return usuario.grupos

    @staticmethod
    def adicionar_membro_por_convite(codigo_convite, id_usuario):
        grupo = Grupo.query.filter_by(codigo_convite=codigo_convite).first()
        if not grupo:
            return None, "Grupo não encontrado com esse código."

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return None, "Usuário não encontrado."

        if usuario in grupo.membros:
            return grupo, None  # já é membro

        grupo.membros.append(usuario)
        banco.session.commit()
        return grupo, None

    @staticmethod
    def remover_membro(grupo_id, usuario_id):
        grupo = Grupo.query.get(grupo_id)
        usuario = Usuario.query.get(usuario_id)
        if not grupo or not usuario:
            return False
        if usuario in grupo.membros:
            grupo.membros.remove(usuario)
            banco.session.commit()
            return True
        return False

    @staticmethod
    def verificar_membro(grupo_id, usuario_id):
        grupo = Grupo.query.get(grupo_id)
        usuario = Usuario.query.get(usuario_id)
        if not grupo or not usuario:
            return False
        return usuario in grupo.membros
