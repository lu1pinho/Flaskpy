from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db
from datetime import date

convenio_bp = Blueprint('convenio', __name__, url_prefix='/convenio')

@convenio_bp.route('/', methods=['GET'])
def get_convenios():
    try:
        select_query = text('SELECT id_convenio, nome_convenio, cnpj FROM "Convenio" ORDER BY id_convenio')
        result = db.session.execute(select_query).fetchall()
        convenios = [
            {"id_convenio": row[0], "nome_convenio": row[1], "cnpj": row[2]}
            for row in result
        ]
        return jsonify(convenios), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao buscar convênios.",
            "details": str(e)
        }), 500

@convenio_bp.route('/<int:id_convenio>', methods=['GET'])
def get_convenio(id_convenio):
    try:
        select_query = text('SELECT id_convenio, nome_convenio, cnpj FROM "Convenio" WHERE id_convenio = :id')
        result = db.session.execute(select_query, {'id': id_convenio}).fetchone()
        if not result:
            return jsonify({"message": "Convênio não encontrado."}), 404
        convenio = {"id_convenio": result[0], "nome_convenio": result[1], "cnpj": result[2]}
        return jsonify(convenio), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao buscar convênio.",
            "details": str(e)
        }), 500

@convenio_bp.route('/', methods=['POST'])
def create_convenio():
    try:
        data = request.get_json()
        nome_convenio = data.get('nome_convenio')
        cnpj = data.get('cnpj')

        if not nome_convenio or not cnpj:
            return jsonify({"message": "Campos nome_convenio e cnpj são obrigatórios."}), 400

        insert_query = text('''
            INSERT INTO "Convenio" (nome_convenio, cnpj)
            VALUES (:nome_convenio, :cnpj)
            RETURNING id_convenio
        ''')
        result = db.session.execute(insert_query, {'nome_convenio': nome_convenio, 'cnpj': cnpj})
        novo_id = result.fetchone()[0]
        db.session.commit()

        return jsonify({
            "message": "Convênio criado com sucesso.",
            "id_convenio": novo_id
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Erro ao criar convênio.",
            "details": str(e)
        }), 500

@convenio_bp.route('/', methods=['PUT'])
def update_convenio():
    try:
        data = request.get_json()
        id_convenio = data.get('id_convenio')
        nome_convenio = data.get('nome_convenio')
        cnpj = data.get('cnpj')

        if not nome_convenio and not cnpj:
            return jsonify({"message": "Informe pelo menos um campo para atualizar (nome_convenio ou cnpj)."}), 400

        update_parts = []
        params = {'id': id_convenio}

        if nome_convenio:
            update_parts.append('nome_convenio = :nome_convenio')
            params['nome_convenio'] = nome_convenio
        if cnpj:
            update_parts.append('cnpj = :cnpj')
            params['cnpj'] = cnpj

        update_query = text(f'''
            UPDATE "Convenio"
            SET {', '.join(update_parts)}
            WHERE id_convenio = :id
        ''')

        result = db.session.execute(update_query, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Convênio não encontrado para atualização."}), 404

        return jsonify({"message": "Convênio atualizado com sucesso."}), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao atualizar convênio.",
            "details": str(e)
        }), 500

@convenio_bp.route('/<int:id_convenio>', methods=['DELETE'])
def delete_convenio(id_convenio):
    try:
        delete_query = text('DELETE FROM "Convenio" WHERE id_convenio = :id')
        result = db.session.execute(delete_query, {'id': id_convenio})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Convênio não encontrado para exclusão."}), 404

        return jsonify({"message": "Convênio excluído com sucesso."}), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao excluir convênio.",
            "details": str(e)
        }), 500


@convenio_bp.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    try:
        query = text("""
            SELECT 
                c.nome_convenio,
                COUNT(DISTINCT p.id_paciente) AS quantidade
            FROM "Convenio" c
            JOIN "Paciente" p ON p.id_convenio = c.id_convenio
            GROUP BY c.nome_convenio
            ORDER BY quantidade DESC
        """)

        resultado = db.session.execute(query).mappings().all()

        total = sum(row['quantidade'] for row in resultado) or 1

        top3 = resultado[:3]
        outros = resultado[3:]

        percentual_top3 = [
            {
                'nome_convenio': row['nome_convenio'],
                'percentual': round((row['quantidade'] / total) * 100, 2)
            }
            for row in top3
        ]

        percentual_outros = round((sum(row['quantidade'] for row in outros) / total) * 100, 2)

        if percentual_outros > 0:
            percentual_top3.append({
                'nome_convenio': 'Outros',
                'percentual': percentual_outros
            })

        return jsonify(percentual_top3)

    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500

