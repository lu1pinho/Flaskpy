from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

consulta_bp = Blueprint('consulta', __name__, url_prefix='/consulta')

@consulta_bp.route('/', methods=['GET'])
def get_consultas():
    try:
        select_query = text('''
            SELECT id_consulta, id_paciente, id_med, especialidade, hora_consulta, data_consulta, valor_consulta
            FROM "Consulta" ORDER BY id_consulta
        ''')
        result = db.session.execute(select_query).fetchall()
        consultas = [
            {
                "id_consulta": row[0],
                "id_paciente": row[1],
                "id_med": row[2],
                "especialidade": row[3],
                "hora_consulta": row[4].isoformat() if row[4] else None,
                "data_consulta": row[5].isoformat() if row[5] else None,
                "valor_consulta": row[6]
            } for row in result
        ]
        return jsonify(consultas), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao buscar consultas.",
            "details": str(e)
        }), 500

@consulta_bp.route('/<int:id_consulta>', methods=['GET'])
def get_consulta(id_consulta):
    try:
        select_query = text('''
            SELECT id_consulta, id_paciente, id_med, especialidade, hora_consulta, data_consulta, valor_consulta
            FROM "Consulta" WHERE id_consulta = :id
        ''')
        result = db.session.execute(select_query, {'id': id_consulta}).fetchone()
        if not result:
            return jsonify({"message": "Consulta não encontrada."}), 404
        consulta = {
            "id_consulta": result[0],
            "id_paciente": result[1],
            "id_med": result[2],
            "especialidade": result[3],
            "hora_consulta": result[4].isoformat() if result[4] else None,
            "data_consulta": result[5].isoformat() if result[5] else None,
            "valor_consulta": result[6]
        }
        return jsonify(consulta), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao buscar consulta.",
            "details": str(e)
        }), 500

@consulta_bp.route('/', methods=['POST'])
def create_consulta():
    try:
        data = request.get_json()
        id_paciente = data.get('id_paciente')
        id_med = data.get('id_med')
        especialidade = data.get('especialidade')
        hora_consulta = data.get('hora_consulta')
        data_consulta = data.get('data_consulta')
        valor_consulta = data.get('valor_consulta')

        if not all([id_paciente, id_med, especialidade, hora_consulta, data_consulta, valor_consulta]):
            return jsonify({"message": "Todos os campos são obrigatórios."}), 400

        insert_query = text('''
            INSERT INTO "Consulta" (id_paciente, id_med, especialidade, hora_consulta, data_consulta, valor_consulta)
            VALUES (:id_paciente, :id_med, :especialidade, :hora_consulta, :data_consulta, :valor_consulta)
            RETURNING id_consulta
        ''')
        result = db.session.execute(insert_query, {
            'id_paciente': id_paciente,
            'id_med': id_med,
            'especialidade': especialidade,
            'hora_consulta': hora_consulta,
            'data_consulta': data_consulta,
            'valor_consulta': valor_consulta
        })
        novo_id = result.fetchone()[0]
        db.session.commit()

        return jsonify({
            "message": "Consulta criada com sucesso.",
            "id_consulta": novo_id
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Erro ao criar consulta.",
            "details": str(e)
        }), 500

@consulta_bp.route('/', methods=['PUT'])
def update_consulta():
    try:
        data = request.get_json()
        id_consulta = data.get('id_consulta')
        if not id_consulta:
            return jsonify({"message": "Campo id_consulta é obrigatório para atualização."}), 400

        # Campos opcionais para atualizar
        id_paciente = data.get('id_paciente')
        id_med = data.get('id_med')
        especialidade = data.get('especialidade')
        hora_consulta = data.get('hora_consulta')
        data_consulta = data.get('data_consulta')
        valor_consulta = data.get('valor_consulta')

        if not any([id_paciente, id_med, especialidade, hora_consulta, data_consulta, valor_consulta]):
            return jsonify({"message": "Informe pelo menos um campo para atualizar."}), 400

        update_parts = []
        params = {'id': id_consulta}

        if id_paciente is not None:
            update_parts.append('id_paciente = :id_paciente')
            params['id_paciente'] = id_paciente
        if id_med is not None:
            update_parts.append('id_med = :id_med')
            params['id_med'] = id_med
        if especialidade is not None:
            update_parts.append('especialidade = :especialidade')
            params['especialidade'] = especialidade
        if hora_consulta is not None:
            update_parts.append('hora_consulta = :hora_consulta')
            params['hora_consulta'] = hora_consulta
        if data_consulta is not None:
            update_parts.append('data_consulta = :data_consulta')
            params['data_consulta'] = data_consulta
        if valor_consulta is not None:
            update_parts.append('valor_consulta = :valor_consulta')
            params['valor_consulta'] = valor_consulta

        update_query = text(f'''
            UPDATE "Consulta"
            SET {', '.join(update_parts)}
            WHERE id_consulta = :id
        ''')

        result = db.session.execute(update_query, params)
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Consulta não encontrada para atualização."}), 404

        return jsonify({"message": "Consulta atualizada com sucesso."}), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao atualizar consulta.",
            "details": str(e)
        }), 500

@consulta_bp.route('/<int:id_consulta>', methods=['DELETE'])
def delete_consulta(id_consulta):
    try:
        delete_query = text('DELETE FROM "Consulta" WHERE id_consulta = :id')
        result = db.session.execute(delete_query, {'id': id_consulta})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({"message": "Consulta não encontrada para exclusão."}), 404

        return jsonify({"message": "Consulta excluída com sucesso."}), 200
    except Exception as e:
        return jsonify({
            "message": "Erro ao excluir consulta.",
            "details": str(e)
        }), 500