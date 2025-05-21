from flask import Blueprint, request
from services.grupo_service import GrupoService
from models import banco
from models.grupo import Grupo
from models.usuario import Usuario
from utils.response import sucesso, erro
import secrets
import string

controlador_grupo = Blueprint("controlador_grupo", __name__)

def gerar_codigo_convite():
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))

@controlador_grupo.route("/grupos", methods=["GET", "POST", "OPTIONS"])
def grupos():
    if request.method == "OPTIONS":
        return '', 200

    if request.method == "GET":
        usuario_id = request.args.get("usuario_id")
        grupos = GrupoService.listar_grupos_por_usuario(usuario_id)
        if grupos is None:
            return erro("Usuário não encontrado", 404)
        return sucesso([{
            "id": g.id,
            "nome": g.nome,
            "codigo_convite": g.codigo_convite,
            "membros": [{"id": m.id, "nome": m.nome, "email": m.email} for m in g.membros]
        }])

    if request.method == "POST":
        dados = request.json
        nome = dados.get("nome")
        descricao = dados.get("descricao")
        regras = dados.get("regras")
        membros_emails = dados.get("membros", [])

        if not nome or not regras:
            return erro("Nome e regras são obrigatórios.", 400)

        codigo_convite = gerar_codigo_convite()
        while Grupo.query.filter_by(codigo_convite=codigo_convite).first():
            codigo_convite = gerar_codigo_convite()

        try:
            grupo = Grupo(nome=nome, descricao=descricao, regras=regras, codigo_convite=codigo_convite)
            banco.session.add(grupo)
            banco.session.flush()

            id_criador = dados.get("id_criador")
            if id_criador:
                criador = Usuario.query.get(id_criador)
                if criador:
                    grupo.membros.append(criador)

            for email in membros_emails:
                usuario = Usuario.query.filter_by(email=email).first()
                if usuario and usuario not in grupo.membros:
                    grupo.membros.append(usuario)

            banco.session.commit()

        except Exception as e:
            banco.session.rollback()
            return erro(f"Erro ao criar grupo: {str(e)}", 500)

        return sucesso({
            'id': grupo.id,
            'nome': grupo.nome,
            'descricao': grupo.descricao,
            'regras': grupo.regras,
            'codigo_convite': grupo.codigo_convite,
            'membros': [u.email for u in grupo.membros]
        })

@controlador_grupo.route("/grupos/<int:grupo_id>", methods=["GET", "OPTIONS"])
def grupo_detalhes(grupo_id):
    if request.method == "OPTIONS":
        return '', 200
    grupo = Grupo.query.get(grupo_id)
    if not grupo:
        return erro("Grupo não encontrado", 404)
    return sucesso({
        'id': grupo.id,
        'nome': grupo.nome,
        'descricao': grupo.descricao,
        'regras': grupo.regras,
        'codigo_convite': grupo.codigo_convite,
        'membros': [{'email': m.email} for m in grupo.membros]
    })

@controlador_grupo.route("/usuarios/<int:usuario_id>/grupos", methods=["GET", "OPTIONS"])
def usuario_grupos(usuario_id):
    if request.method == "OPTIONS":
        return '', 200
    grupos = GrupoService.listar_grupos_por_usuario(usuario_id)
    if grupos is None:
        return erro("Usuário não encontrado", 404)
    return sucesso([{
        "id": g.id,
        "nome": g.nome,
        "codigo_convite": g.codigo_convite,
        "membros": [{"id": m.id, "nome": m.nome, "email": m.email} for m in g.membros]
    } for g in grupos])

@controlador_grupo.route("/grupos/<int:grupo_id>/membros", methods=["POST", "OPTIONS"])
def adicionar_membro(grupo_id):
    if request.method == "OPTIONS":
        return '', 200
    dados = request.json
    grupo, erro_msg = GrupoService.adicionar_membro_por_convite(
        codigo_convite=dados.get("codigo_convite"),
        id_usuario=dados.get("id_usuario")
    )
    if erro_msg:
        return erro(erro_msg, 404)
    return sucesso({"grupo_id": grupo.id, "mensagem": "Usuário adicionado"})

@controlador_grupo.route("/grupos/<int:grupo_id>/membros/<int:usuario_id>", methods=["DELETE", "OPTIONS"])
def remover_membro(grupo_id, usuario_id):
    if request.method == "OPTIONS":
        return '', 200
    ok = GrupoService.remover_membro(grupo_id, usuario_id)
    if ok:
        return sucesso({"mensagem": "Removido com sucesso"})
    return erro("Usuário ou grupo inválido", 404)

@controlador_grupo.route("/grupos/<int:grupo_id>/membros/<int:usuario_id>/verificar", methods=["GET", "OPTIONS"])
def verificar_membro(grupo_id, usuario_id):
    if request.method == "OPTIONS":
        return '', 200
    membro = GrupoService.verificar_membro(grupo_id, usuario_id)
    return sucesso({"membro": membro})

@controlador_grupo.route("/grupos/entrar", methods=["POST", "OPTIONS"])
def entrar_grupo_por_convite():
    if request.method == "OPTIONS":
        return '', 200
    dados = request.json
    codigo_convite = dados.get("codigo_convite", "").upper()
    id_usuario = dados.get("id_usuario")
    if not codigo_convite or not id_usuario:
        return erro("Código de convite e ID do usuário são obrigatórios", 400)
    grupo, erro_msg = GrupoService.adicionar_membro_por_convite(
        codigo_convite=codigo_convite,
        id_usuario=id_usuario
    )
    if erro_msg:
        return erro(erro_msg, 404)
    return sucesso({
        "id": grupo.id,
        "nome": grupo.nome,
        "codigo_convite": grupo.codigo_convite,
        "membros": [{"id": m.id, "nome": m.nome, "email": m.email} for m in grupo.membros]
    })
