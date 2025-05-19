from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

paciente_bp = Blueprint('paciente', __name__, url_prefix='/paciente')

@paciente_bp.route('/', methods=['GET'])
def paciente_index():
    try:
        result = db.session.execute(text('SELECT * FROM "Paciente"'))
        rows = result.fetchall()
        if not rows:
            return jsonify({"ERRO": "Nenhum paciente encontrado"}), 404
        pacientes = [dict(row._mapping) for row in rows]
        return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"ERRO": str(e)}), 500

@paciente_bp.route('/<int:id_paciente>', methods=['GET'])
def paciente_search_by_id(id_paciente):
    try:
        sql = text('SELECT * FROM "Paciente" WHERE id_paciente = :id_paciente')
        result = db.session.execute(sql, {'id_paciente': id_paciente})
        row = result.fetchone()

        if row is None:
            return jsonify({"error": "Paciente não encontrado"}), 404

        paciente_data = dict(row._mapping)
        return jsonify(paciente_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@paciente_bp.route('/', methods=['POST'])
def paciente_create():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'nome_paciente': data.get('nome_paciente'),
            'cpf_paciente': data.get('cpf_paciente'),
            'rg_paciente': data.get('rg_paciente'),
            'nasc_paciente': data.get('nasc_paciente'),
            'contact_paciente': data.get('contact_paciente'),
            'email_paciente': data.get('email_paciente'),  # correto aqui
            'end_paciente': data.get('end_paciente'),
            'hist_paciente': data.get('hist_paciente'),
            'id_convenio': data.get('id_convenio')
        }

        if any(value is None for value in params.values()):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            '''INSERT INTO "Paciente" (nome_paciente, cpf_paciente, rg_paciente, nasc_paciente, 
             contact_paciente, email_paciente, end_paciente, hist_paciente, id_convenio)
            VALUES (:nome_paciente, :cpf_paciente, :rg_paciente, :nasc_paciente, 
             :contact_paciente, :email_paciente, :end_paciente, 
             :hist_paciente, :id_convenio)'''
        )

        db.session.execute(sql, params)
        db.session.commit()

        return jsonify({"message": "Paciente cadastrado com sucesso"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@paciente_bp.route('/<int:id_paciente>', methods=['DELETE'])
def paciente_delete(id_paciente):
    try:
        sql = text('DELETE FROM "Paciente" WHERE id_paciente = :id_paciente')
        result = db.session.execute(sql, {'id_paciente': id_paciente})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Paciente não encontrado"}), 404

        return jsonify({"message": "Deletado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@paciente_bp.route('/', methods=['PUT'])
def paciente_update():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'id_paciente': data.get('id_paciente'),
            'nome_paciente': data.get('nome_paciente'),
            'cpf_paciente': data.get('cpf_paciente'),
            'rg_paciente': data.get('rg_paciente'),
            'nasc_paciente': data.get('nasc_paciente'),
            'contact_paciente': data.get('contact_paciente'),
            'email_paciente': data.get('email_paciente'),
            'end_paciente': data.get('end_paciente'),
            'hist_paciente': data.get('hist_paciente'),
            'id_convenio': data.get('id_convenio')
        }

        if any(value is None for key, value in params.items() if key != 'id_paciente'):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            'UPDATE "Paciente" SET nome_paciente = :nome_paciente, cpf_paciente = :cpf_paciente, rg_paciente = :rg_paciente, nasc_paciente = :nasc_paciente, contact_paciente = :contact_paciente, email_paciente = :email_paciente, end_paciente = :end_paciente, hist_paciente = :hist_paciente, id_convenio = :id_convenio WHERE id_paciente = :id_paciente'
        )

        result = db.session.execute(sql, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Paciente não encontrado"}), 404

        return jsonify({"message": "Paciente atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
