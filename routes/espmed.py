from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db

espmed_bp = Blueprint('espmed', __name__, url_prefix='/espmed')

@espmed_bp.route('/', methods=['GET'])
def get_all_esp_med():
    try:
        result = db.session.execute(text('SELECT * FROM "Esp_med"'))
        rows = result.fetchall()
        if not rows:
            return jsonify({"message": "Nenhuma especialidade vinculada a um médico."}), 204
        return jsonify([dict(row._mapping) for row in rows]), 200
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao buscar especialidades vinculadas a médicos.",
            "details": str(e)
        }), 500

@espmed_bp.route('/', methods=['GET'])
def getbyid():
    try:
        id_medico = request.args.get('id_medico', type=int)

        if id_medico is None:
            return jsonify({'error': 'Parâmetro id_medico é obrigatório'}), 400

        especialidades = EspecialidadeMedico.query.filter_by(id_med=id_medico).all()

        resultado = [
            {
                'id_especialidade': espmed.id_esp,
                'id_medico': espmed.id_med
            }
            for espmed in especialidades
        ]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@espmed_bp.route('/', methods=['POST'])
def create_esp_med():
    try:
        data = request.get_json()
        id_med = data.get('id_med')
        id_esp = data.get('id_esp')

        if not id_med or not id_esp:
            return jsonify({"message": "Os campos id_med e id_esp são obrigatórios."}), 400

        query = text('INSERT INTO "Esp_med" (id_med, id_esp) VALUES (:id_med, :id_esp)')
        db.session.execute(query, {'id_med': id_med, 'id_esp': id_esp})
        db.session.commit()

        return jsonify({
            "message": f"Médico {id_med} vinculado com sucesso à especialidade {id_esp}."
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao cadastrar o vínculo médico-especialidade.",
            "details": str(e)
        }), 500

@espmed_bp.route('/', methods=['PUT'])
def update_esp_med():
    try:
        data = request.get_json()
        id_med = data.get('id_med')
        antigo_id_esp = data.get('antigo_id_esp')
        novo_id_esp = data.get('novo_id_esp')

        if not id_med or not antigo_id_esp or not novo_id_esp:
            return jsonify({"message": "Os campos id_med, antigo_id_esp e novo_id_esp são obrigatórios."}), 400

        with db.session.begin():
            delete_query = text('''
                DELETE FROM "Esp_med"
                WHERE id_med = :id_med AND id_esp = :antigo_id_esp
            ''')
            result_delete = db.session.execute(delete_query, {
                'id_med': id_med,
                'antigo_id_esp': antigo_id_esp
            })

            if result_delete.rowcount == 0:
                return jsonify({"message": "Vínculo antigo não encontrado para exclusão."}), 404

            insert_query = text('''
                INSERT INTO "Esp_med" (id_med, id_esp)
                VALUES (:id_med, :novo_id_esp)
            ''')
            db.session.execute(insert_query, {
                'id_med': id_med,
                'novo_id_esp': novo_id_esp
            })

        return jsonify({
            "message": "Especialidade atualizada com sucesso.",
            "id_antigo_esp": antigo_id_esp,
            "id_novo_esp": novo_id_esp,
            "id_med": id_med
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Erro interno ao atualizar o vínculo.",
            "details": str(e)
        }), 500

@espmed_bp.route('/', methods=['DELETE'])
def delete_esp_med():
    try:
        data = request.get_json()
        id_med = data.get('id_med')
        id_esp = data.get('id_esp')

        if not id_med or not id_esp:
            return jsonify({"message": "id_med e id_esp são obrigatórios para remover o vínculo."}), 400

        query = text('DELETE FROM "Esp_med" WHERE id_med = :id_med AND id_esp = :id_esp')
        result = db.session.execute(query, {'id_med': id_med, 'id_esp': id_esp})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({
                "message": f"Nenhum vínculo encontrado entre médico {id_med} e especialidade {id_esp}."
            }), 404

        return jsonify({
            "message": f"Vínculo entre médico {id_med} e especialidade {id_esp} removido com sucesso."
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Erro interno ao remover vínculo médico-especialidade.",
            "details": str(e)
        }), 500