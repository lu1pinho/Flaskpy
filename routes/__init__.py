from .consultas import consulta_bp
from .convenio import convenio_bp
from .especialidade import esp_bp
from .espmed import espmed_bp
from .medico import medico_bp
from .paciente import paciente_bp
from .user import user_bp

all_blueprints = [
    user_bp,
    paciente_bp,
    medico_bp,
    espmed_bp,
    esp_bp,
    convenio_bp,
    consulta_bp,
]