from flask import jsonify

def sucesso(data=None, message=None, status=200):
    """
    Retorna uma resposta de sucesso no formato padrão.
    """
    resposta = {
        "success": True
    }
    if data is not None:
        resposta["data"] = data
    if message:
        resposta["message"] = message
    return jsonify(resposta), status

def erro(message="Erro interno do servidor", status=500):
    """
    Retorna uma resposta de erro no formato padrão.
    """
    resposta = {
        "success": False,
        "message": message
    }
    return jsonify(resposta), status
