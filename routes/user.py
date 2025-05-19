from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/', methods=['GET'])
def user_index():
    try:
        result = db.session.execute(text('SELECT * FROM "Usuario"'))
        rows = result.fetchall()
        if not rows:
            return jsonify({"ERRO": "Nenhum usuário encontrado"}), 404
        users = [dict(row._mapping) for row in rows]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"ERRO": str(e)}), 500

@user_bp.route('/<int:id_usuario>', methods=['GET'])
def user_search_by_id(id_usuario):
    try:
        sql = text('SELECT * FROM "Usuario" WHERE id_usuario = :id_usuario')
        result = db.session.execute(sql, {'id_usuario': id_usuario})
        row = result.fetchone()

        if row is None:
            return jsonify({"error": "Usuário não encontrado"}), 404

        user_data = dict(row._mapping)
        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/', methods=['POST'])
def user_create():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'email': data.get('email'),
            'senha': data.get('senha'),
            'tipo_usuario': data.get('tipo_usuario')
        }

        if any(value is None for value in params.values()):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            'INSERT INTO "Usuario" (email, senha, tipo_usuario, atualizado_em) VALUES (:email, :senha, :tipo_usuario, NOW())'
        )

        db.session.execute(sql, params)
        db.session.commit()

        return jsonify({"message": "Usuário criado com sucesso"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<int:id_usuario>', methods=['DELETE'])
def user_delete(id_usuario):
    try:
        sql = text('DELETE FROM "Usuario" WHERE id_usuario = :id_usuario')
        result = db.session.execute(sql, {'id_usuario': id_usuario})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify({"message": "Deletado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/', methods=['PUT'])
def user_update():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio ou inválido"}), 400

        params = {
            'email': data.get('email'),
            'senha': data.get('senha'),
            'tipo_usuario': data.get('tipo_usuario'),
            'id_usuario': data.get('id_usuario')
        }

        if any(value is None for key, value in params.items() if key != 'id_usuario'):
            return jsonify({"error": "Dados incompletos"}), 400

        sql = text(
            'UPDATE "Usuario" SET email = :email, senha = :senha, tipo_usuario = :tipo_usuario, atualizado_em = NOW() '
            'WHERE id_usuario = :id_usuario'
        )

        result = db.session.execute(sql, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify({"message": "Usuário atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




