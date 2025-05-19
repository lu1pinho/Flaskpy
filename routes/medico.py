from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

@medico_bp.route('/', methods=['GET'])
def medico_index():
    try:
        result = db.session.execute(text('SELECT * FROM "Medico"'))
        rows = result.fetchall()
        if not rows:
            return jsonify({"error": "Nenhum médico encontrado"}), 404
        medicos = [dict(row._mapping) for row in rows]
        return jsonify(medicos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medico_bp.route('/<int:id_med>', methods=['GET'])
def medico_search_by_id(id_med):
    try:
        sql = text('SELECT * FROM "Medico" WHERE id_med = :id_med')
        result = db.session.execute(sql, {'id_med': id_med})
        row = result.fetchone()

        if row is None:
            return jsonify({"error": "Médico não encontrado"}), 404

        medico_data = dict(row._mapping)
        return jsonify(medico_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medico_bp.route('/', methods=['POST'])
def medico_create():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'nome_med': data.get('nome_med'),
            'turno': data.get('turno'),
            'crm': data.get('crm'),
            'telefone': data.get('telefone'),
            'email_med': data.get('email_med')
        }

        if any(value is None for value in params.values()):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            '''INSERT INTO "Medico" (nome_med, turno, crm, telefone, email_med)
               VALUES (:nome_med, :turno, :crm, :telefone, :email_med)'''
        )

        db.session.execute(sql, params)
        db.session.commit()

        return jsonify({"message": "Médico cadastrado com sucesso"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medico_bp.route('/<int:id_med>', methods=['DELETE'])
def medico_delete(id_med):
    try:
        sql = text('DELETE FROM "Medico" WHERE id_med = :id_med')
        result = db.session.execute(sql, {'id_med': id_med})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Médico não encontrado"}), 404

        return jsonify({"message": "Deletado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medico_bp.route('/', methods=['PUT'])
def medico_update():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'id_med': data.get('id_med'),
            'nome_med': data.get('nome_med'),
            'turno': data.get('turno'),
            'crm': data.get('crm'),
            'telefone': data.get('telefone'),
            'email_med': data.get('email_med')
        }

        if any(value is None for key, value in params.items() if key != 'id_med'):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            '''UPDATE "Medico"
               SET nome_med = :nome_med, turno = :turno, crm = :crm, 
                   telefone = :telefone, email_med = :email_med
               WHERE id_med = :id_med'''
        )

        result = db.session.execute(sql, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Médico não encontrado"}), 404

        return jsonify({"message": "Médico atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500