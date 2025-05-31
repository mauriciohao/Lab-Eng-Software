from flask import Blueprint, request
from models.usuario import Usuario
from models import banco
from utils.response import sucesso, erro
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    username = data.get('username')
    senha = data.get('senha')

    if not all([nome, email, username, senha]):
        return erro('Por favor, preencha todos os campos obrigatórios.', 400)

    if len(username) < 3:
        return erro('O nome de usuário deve ter pelo menos 3 caracteres.', 400)

    if len(senha) < 6:
        return erro('A senha deve ter pelo menos 6 caracteres.', 400)

    if Usuario.query.filter_by(email=email).first():
        return erro('Este email já está cadastrado.', 400)

    if Usuario.query.filter_by(username=username).first():
        return erro('Este nome de usuário já está em uso.', 400)

    try:
        novo_usuario = Usuario(nome=nome, email=email, username=username, senha=senha)
        banco.session.add(novo_usuario)
        banco.session.commit()
        return sucesso(message='Cadastro realizado com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {str(e)}")
        logger.error(traceback.format_exc())
        banco.session.rollback()
        return erro('Erro ao realizar cadastro. Tente novamente.', 500)

@auth.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    if not request.is_json:
        return erro('Content-Type must be application/json', 415)

    data = request.get_json()
    login_id = data.get('loginId')
    senha = data.get('password')

    if not login_id or not senha:
        return erro('Dados incompletos', 400)

    try:
        user = Usuario.query.filter_by(email=login_id, senha=senha).first()
        if not user:
            user = Usuario.query.filter_by(username=login_id, senha=senha).first()

        if not user:
            return erro('Email/usuário ou senha inválidos!', 401)

        return sucesso({
            'id': user.id,
            'nome': user.nome,
            'email': user.email,
            'username': user.username
        }, message='Login bem-sucedido')
    except Exception as e:
        logger.error(f"Erro ao consultar banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        return erro('Erro interno ao realizar login', 500)
