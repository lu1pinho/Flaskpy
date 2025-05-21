import os
from flask import Flask, jsonify, request, render_template
from extensions import db
from routes import all_blueprints
from dotenv import load_dotenv

from livereload import Server

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise RuntimeError("A variável de ambiente DATABASE_URL não está definida.")

    db.init_app(app)

    for bp in all_blueprints:
        app.register_blueprint(bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.debug = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    server = Server(app.wsgi_app)
    server.watch('templates/index.html')
    # server.watch('templates/login.html')


    server.serve(port=5000, host='127.0.0.1')
