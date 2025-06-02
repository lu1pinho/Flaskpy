import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from sqlalchemy import text
from extensions import db
from routes import all_blueprints
from dotenv import load_dotenv
from livereload import Server

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise RuntimeError("A variável de ambiente DATABASE_URL não está definida.")

    db.init_app(app)

    for bp in all_blueprints:
        app.register_blueprint(bp)

    # Página principal
    @app.route('/')
    def index_page():
        # Total de pacientes
        query_pacientes = text('SELECT COUNT(*) FROM "Paciente"')
        total_pacientes = db.session.execute(query_pacientes).scalar()

        # Total de consultas atendidas no mês atual
        now = datetime.now()
        query_atendidos_mes = text('''
            SELECT COUNT(*) FROM "Consulta"
            WHERE status = 'atendido'
            AND EXTRACT(YEAR FROM data_consulta) = :ano
            AND EXTRACT(MONTH FROM data_consulta) = :mes
        ''')
        total_atendidos_mes = db.session.execute(query_atendidos_mes, {'ano': now.year, 'mes': now.month}).scalar()

        total_medicos = db.session.execute(text('SELECT COUNT(*) FROM "Medico"')).scalar()

        total_medicos_ativos = db.session.execute(
            text(
                "SELECT COUNT(DISTINCT id_med) AS total_medicos_ativos FROM \"Consulta\" WHERE data_consulta >= CURRENT_DATE - INTERVAL '30 days' AND status = 'atendido'")
        ).scalar()

        total_consultas_hoje = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM "Consulta"
            WHERE DATE(data_consulta) = CURRENT_DATE
        """)).scalar()

        total_consultas_pendentes_hoje = db.session.execute(text("""
            SELECT COUNT(*)
            FROM "Consulta"
            WHERE DATE(data_consulta) = CURRENT_DATE
              AND status = 'pendente'
        """)).scalar()

        faturamento_atual = db.session.execute(text("""
            SELECT COALESCE(SUM(valor_consulta), 0)
            FROM "Consulta"
            WHERE status = 'atendido'
              AND DATE_TRUNC('month', data_consulta) = DATE_TRUNC('month', CURRENT_DATE)
        """)).scalar()

        faturamento_anterior = db.session.execute(text("""
            SELECT COALESCE(SUM(valor_consulta), 0)
            FROM "Consulta"
            WHERE status = 'atendido'
              AND DATE_TRUNC('month', data_consulta) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
        """)).scalar()

        if faturamento_anterior == 0:
            faturamento_superior = 100 if faturamento_atual > 0 else 0
        else:
            faturamento_superior = ((faturamento_atual - faturamento_anterior) / faturamento_anterior) * 100

        return render_template('index.html',
                               total_pacientes=total_pacientes,
                               total_atendidos_mes=total_atendidos_mes,
                               total_medicos=total_medicos,
                               total_medicos_ativos=total_medicos_ativos,
                               total_consultas_hoje=total_consultas_hoje,
                               total_consultas_pendentes_hoje=total_consultas_pendentes_hoje,
                               faturamento_atual=faturamento_atual,
                               faturamento_superior=faturamento_superior)

    # Tela de login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')

            dados, status = autenticar_usuario(email, senha)

            if status == 200:
                session['usuario'] = {
                    'id': dados['id'],
                    'email': dados['email']
                }
                return redirect(url_for('index_page'))
            else:
                erro = dados.get('error', 'Erro desconhecido')
                return render_template('login.html', erro=erro)

        return render_template('login.html')

    # Lógica interna para autenticar usuário sem depender de API externa
    def autenticar_usuario(email, senha):
        if not email or not senha:
            return {"error": "Email/Senha incompleto"}, 400

        sql = text('SELECT id_usuario, email, senha FROM "Usuario" WHERE email = :email')
        result = db.session.execute(sql, {'email': email})
        row = result.mappings().fetchone()

        if not row:
            return {"error": "Usuário não encontrado"}, 404

        if row['senha'] != senha:
            return {"error": "Senha incorreta"}, 401

        return {
            "id": row['id_usuario'],
            "email": row['email'],
            "autenticado": True
        }, 200

    @app.route('/view/pacientes', methods=['GET', 'POST'])
    def view_pacientes():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        else:
            return render_template('pacientes.html')

    @app.route('/view/paciente/cadastro', methods=['GET', 'POST'])
    def view_paciente_cadastro():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        else:
            return render_template('cadastro_paciente.html')

    @app.route('/view/paciente/', methods=['GET', 'POST'])
    def view_paciente():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        else:
            return render_template('pacientes.html')

    @app.route('/paciente_info')
    def paciente_info():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        return render_template('info_paciente.html')

    @app.route('/view/medico', methods=['GET'])
    def view_medico():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        else:
            return render_template('medicos.html')

    @app.route('/view/medico/cadastro', methods=['GET'])
    def view_medico_cadastro():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        return render_template('cadastro_medico.html')

    @app.route('/medico_info')
    def medico_info():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        return render_template('info_medico.html')

    @app.route('/view/convenios', methods=['GET'])
    def convenios():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        return render_template('convenios.html')

    @app.route('/view/agendamentos/', methods=['GET'])
    def agendamentos():
        if not session.get('usuario'):
            return redirect(url_for('login'))
        else:
            return render_template('cadastro_agendamento.html')


    return app

if __name__ == '__main__':
    app = create_app()
    app.debug = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    server = Server(app.wsgi_app)
    server.watch('templates/index.html')
    server.watch('templates/login.html')
    server.watch('templates/cadastro_paciente.html')
    server.watch('templates/medico.html')
    server.watch('templates/info_paciente.html')
    server.watch('templates/info_medico.html')
    server.watch('templates/cadastro_medico.html')
    server.watch('templates/cadastro_agendamento.html')

    server.serve(port=5000, host='127.0.0.1')