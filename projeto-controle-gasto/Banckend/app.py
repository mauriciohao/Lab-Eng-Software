# app.py

from flask import Flask, jsonify
from flask_cors import CORS
from models import banco
from models.usuario import Usuario
from controllers.controlador_grupo import controlador_grupo
from controllers.controlador_despesa import controlador_despesa
from controllers.auth import auth
import logging
import os

# Configurar logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Criar instância do app Flask
app = Flask(__name__)

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Inicializar extensões
CORS(app, supports_credentials=True)
banco.init_app(app)

# Tratamento de erros globais
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Endpoint não encontrado."}), 404

@app.errorhandler(500)
def erro_interno(e):
    logger.error(f"Erro interno: {str(e)}")
    return jsonify({"success": False, "message": "Erro interno do servidor."}), 500

# Registrar Blueprints
app.register_blueprint(controlador_grupo, url_prefix='/api')
app.register_blueprint(controlador_despesa, url_prefix='/api')
app.register_blueprint(auth, url_prefix='/api')

# Banco em modo desenvolvimento
def init_db():
    with app.app_context():
        from models.usuario import Usuario
        banco.drop_all()
        banco.create_all()
        logger.info("📦 Banco recriado com sucesso!")
        count = Usuario.query.count()
        logger.info(f"👥 Usuários no banco: {count}")

if __name__ == '__main__':
    modo = os.environ.get("FLASK_ENV", "development")
    logger.info(f"🚀 Iniciando aplicação em modo {modo.upper()}")

    init_db()
    app.run(debug=True)

@app.route("/")
def homepage():
    return jsonify({
        "message": "✅ API do Controle de Gastos está ativa!",
        "status": "ok"
    })

@app.route('/init')
def initialize():
    from models.usuario import Usuario
    from models.grupo import Grupo
    from models.despesa import Despesa
    from models.divisao import Divisao
    banco.create_all()
    return '✅ Banco inicializado com sucesso!'


DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
DEBUG_SECRET = os.environ.get("DEBUG_SECRET", "admin123")  # 默认密码

if DEBUG_MODE:
    @app.route("/debug/usuarios", methods=["GET"])
    def debug_usuarios():
        token = request.args.get("token")

        if token != DEBUG_SECRET:
            return jsonify({
                "success": False,
                "message": "Acesso não autorizado. Token inválido."
            }), 403

        usuarios = Usuario.query.all()
        return jsonify([
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "username": u.username,
                "senha_hash": u.senha
            } for u in usuarios
        ])
