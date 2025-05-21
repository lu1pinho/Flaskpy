CREATE TABLE convenio (
    id_convenio SERIAL PRIMARY KEY,
    nome_convenio TEXT NOT NULL UNIQUE,
    cnpj TEXT NOT NULL UNIQUE
);

CREATE TABLE especialidade (
    id_especialidade SERIAL PRIMARY KEY,
    nome_especialidade TEXT NOT NULL UNIQUE
);

CREATE TABLE medico (
    id_med SERIAL PRIMARY KEY,
    nome_med TEXT NOT NULL,
    turno TEXT NOT NULL,
    crm TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL UNIQUE,
    email_med TEXT NOT NULL UNIQUE
);

CREATE TABLE paciente (
    id_paciente SERIAL PRIMARY KEY,
    nome_paciente TEXT NOT NULL,
    cpf_paciente TEXT NOT NULL UNIQUE,
    rg_paciente TEXT NOT NULL UNIQUE,
    nasc_paciente TIMESTAMP NOT NULL,
    contact_paciente TEXT NOT NULL UNIQUE,
    email_paciente TEXT NOT NULL UNIQUE,
    end_paciente TEXT NOT NULL,
    hist_paciente TEXT NOT NULL,
    id_convenio INTEGER REFERENCES convenio(id_convenio) ON DELETE SET NULL
);

CREATE TABLE consulta (
    id_consulta SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL REFERENCES paciente(id_paciente) ON UPDATE CASCADE ON DELETE RESTRICT,
    id_med INTEGER NOT NULL REFERENCES medico(id_med) ON UPDATE CASCADE ON DELETE RESTRICT,
    especialidade TEXT NOT NULL,
    hora_consulta TIMESTAMP NOT NULL,
    data_consulta TIMESTAMP NOT NULL,
    valor_consulta INTEGER NOT NULL
);

CREATE TABLE esp_med (
    id_med INTEGER NOT NULL REFERENCES medico(id_med) ON UPDATE CASCADE ON DELETE RESTRICT,
    id_esp INTEGER NOT NULL REFERENCES especialidade(id_especialidade) ON UPDATE CASCADE ON DELETE RESTRICT,
    PRIMARY KEY (id_med, id_esp)
);

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em TIMESTAMP NOT NULL
);







