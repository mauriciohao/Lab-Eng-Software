from flask import Blueprint, request
from models import banco
from models.despesa import Despesa
from models.divisao import Divisao
from models.usuario import Usuario
from models.grupo import Grupo
from utils.response import sucesso, erro
from datetime import datetime

controlador_despesa = Blueprint('controlador_despesa', __name__)

def converter_data(data_str):
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return None

@controlador_despesa.route('/expenses', methods=['POST', 'OPTIONS'])
def criar_despesa():
    if request.method == 'OPTIONS':
        return '', 200

    dados = request.json
    if not all([dados.get('name'), dados.get('amount'), dados.get('payer_id'), dados.get('group_id')]):
        return erro('Dados incompletos', 400)

    grupo = Grupo.query.get(dados.get('group_id'))
    pagador = Usuario.query.get(dados.get('payer_id'))
    if not grupo or not pagador:
        return erro('Grupo ou pagador não encontrado', 404)

    nova_despesa = Despesa(
        nome=dados.get('name'),
        descricao=dados.get('description'),
        estabelecimento=dados.get('establishment'),
        categoria=dados.get('category'),
        valor=float(dados.get('amount')),
        data=converter_data(dados.get('date')) or datetime.today().date(),
        data_limite=converter_data(dados.get('due_date')),
        grupo_id=dados.get('group_id'),
        pagador_id=dados.get('payer_id'),
        metodo_divisao='manual' if dados.get('settlement_type') == 'manual' else 'igual',
        status='pendente'
    )

    banco.session.add(nova_despesa)
    banco.session.flush()

    if nova_despesa.metodo_divisao == 'igual':
        membros = list(grupo.membros)
        # 只让非付款人平分
        nao_pagadores = [m for m in membros if m.id != pagador.id]
        if nao_pagadores:
            valor_por_membro = nova_despesa.valor / len(nao_pagadores)
            for membro in nao_pagadores:
                banco.session.add(Divisao(
                    despesa_id=nova_despesa.id,
                    usuario_id=membro.id,
                    valor=valor_por_membro
                ))
    else:
        manual_debts = dados.get('manual_debts', {})
        for usuario_id, valor in manual_debts.items():
            try:
                usuario_id = int(usuario_id)
            except (ValueError, TypeError):
                continue
            if usuario_id != pagador.id and valor > 0:
                banco.session.add(Divisao(
                    despesa_id=nova_despesa.id,
                    usuario_id=usuario_id,
                    valor=float(valor)
                ))

    banco.session.commit()
    return sucesso({
        'id': nova_despesa.id,
        'nome': nova_despesa.nome,
        'valor': nova_despesa.valor
    }, message='Despesa criada com sucesso')

@controlador_despesa.route('/groups/<int:grupo_id>/expenses', methods=['GET', 'OPTIONS'])
def listar_despesas_grupo(grupo_id):
    if request.method == 'OPTIONS':
        return '', 200

    grupo = Grupo.query.get(grupo_id)
    if not grupo:
        return erro('Grupo não encontrado', 404)
    despesas = Despesa.query.filter_by(grupo_id=grupo_id).all()
    total_members = len(grupo.membros)  # 新增
    return sucesso([{
        'id': d.id,
        'name': d.nome,
        'description': d.descricao,
        'category': d.categoria,
        'amount': d.valor,
        'date': d.data.strftime('%Y-%m-%d'),
        'due_date': d.data_limite.strftime('%Y-%m-%d') if d.data_limite else None,
        'status': d.status,
        'payer_id': d.pagador_id,
        'debtors_count': banco.session.query(Divisao).filter_by(despesa_id=d.id).count(),
        'total_members': total_members  # 新增
    } for d in despesas])

@controlador_despesa.route('/expenses/<int:despesa_id>', methods=['GET', 'OPTIONS'])
def obter_despesa(despesa_id):
    if request.method == 'OPTIONS':
        return '', 200

    despesa = Despesa.query.get(despesa_id)
    if not despesa:
        return erro('Despesa não encontrada', 404)
    return sucesso({
        'id': despesa.id,
        'name': despesa.nome,
        'description': despesa.descricao,
        'category': despesa.categoria,
        'amount': despesa.valor,
        'date': despesa.data.strftime('%Y-%m-%d'),
        'due_date': despesa.data_limite.strftime('%Y-%m-%d') if despesa.data_limite else None,
        'status': despesa.status,
        'payer_id': despesa.pagador_id,
        'group_id': despesa.grupo_id
    })

@controlador_despesa.route('/expenses/<int:despesa_id>/settlement', methods=['GET', 'OPTIONS'])
def obter_liquidacao(despesa_id):
    if request.method == 'OPTIONS':
        return '', 200

    despesa = Despesa.query.get(despesa_id)
    if not despesa:
        return erro('Despesa não encontrada', 404)
    divisoes = Divisao.query.filter_by(despesa_id=despesa_id).all()
    debitos = {Usuario.query.get(d.usuario_id).nome: d.valor for d in divisoes}
    return sucesso({
        'despesa_id': despesa_id,
        'debts': debitos
    })

@controlador_despesa.route('/expenses/<int:despesa_id>/status', methods=['PUT', 'OPTIONS'])
def atualizar_status(despesa_id):
    if request.method == 'OPTIONS':
        return '', 200

    dados = request.json
    status = dados.get('status')
    if not status:
        return erro('Status não informado', 400)
    despesa = Despesa.query.get(despesa_id)
    if not despesa:
        return erro('Despesa não encontrada', 404)
    despesa.status = status
    banco.session.commit()
    return sucesso({"mensagem": "Status atualizado com sucesso"})
