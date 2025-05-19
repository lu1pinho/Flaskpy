from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

esp_bp = Blueprint('esp', __name__, url_prefix='/esp')

@esp_bp.route('/', methods=['GET'])
def get_especialidades():
    try:
        result = db.session.execute(text('SELECT * FROM "Especialidade"'))
        rows = result.fetchall()
        if not rows:
            return jsonify({"message": "Nenhuma especialidade cadastrada."}), 204
        return jsonify([dict(row._mapping) for row in rows]), 200
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao buscar especialidades.",
            "details": str(e)
        }), 500

@esp_bp.route('/', methods=['POST'])
def create_especialidade():
    try:
        data = request.get_json()
        nome = data.get('nome_especialidade')

        if not nome:
            return jsonify({"message": "O campo nome_especialidade é obrigatório."}), 400

        query = text('''
            INSERT INTO "Especialidade" (nome_especialidade)
            VALUES (:nome_especialidade)
            RETURNING id_especialidade, nome_especialidade
        ''')
        result = db.session.execute(query, {'nome_especialidade': nome})
        db.session.commit()

        return jsonify({
            "message": "Especialidade criada com sucesso.",
            "data": dict(result.fetchone()._mapping)
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao criar especialidade.",
            "details": str(e)
        }), 500

@esp_bp.route('/', methods=['PUT'])
def update_especialidade():
    try:
        data = request.get_json()
        novo_nome = data.get('nome_especialidade')
        id_especialidade = data.get('id_especialidade')

        if not novo_nome or not id_especialidade:
            return jsonify({"message": "Os campos nome_especialidade e id_especialidade são obrigatórios."}), 400

        query = text('''
            UPDATE "Especialidade"
            SET nome_especialidade = :nome
            WHERE id_especialidade = :id
        ''')
        result = db.session.execute(query, {'nome': novo_nome.strip(), 'id': id_especialidade})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Especialidade não encontrada."}), 404

        return jsonify({"message": "Especialidade atualizada com sucesso."}), 200

    except Exception as e:
        return jsonify({
            "message": "Erro interno ao atualizar especialidade.",
            "details": str(e)
        }), 500

@esp_bp.route('/<int:id_especialidade>', methods=['DELETE'])
def delete_especialidade(id_especialidade):
    try:
        query = text('DELETE FROM "Especialidade" WHERE id_especialidade = :id')
        result = db.session.execute(query, {'id': id_especialidade})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Especialidade não encontrada."}), 404

        return jsonify({"message": "Especialidade removida com sucesso."}), 200
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao deletar especialidade.",
            "details": str(e)
        }), 500
