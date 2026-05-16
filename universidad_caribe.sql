 
-- SISTEMA DE GESTIÓN DE MATRÍCULAS — Universidad Caribe
-- DROP DATABASE uninorte;
CREATE DATABASE uninorte;
USE uninorte;

-- BLOQUE 1: SEGURIDAD Y ACCESO

CREATE TABLE rol (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion VARCHAR(255)
);

CREATE TABLE persona (
  id_persona INT AUTO_INCREMENT PRIMARY KEY,
  primer_nombre VARCHAR(50) NOT NULL,
  segundo_nombre VARCHAR(50),
  apellido VARCHAR(50) NOT NULL,
  segundo_apellido VARCHAR(50),
  documento_identidad VARCHAR(50) NOT NULL UNIQUE,
  telefono VARCHAR(20),
  correo VARCHAR(100)
);

CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  correo VARCHAR(100) NOT NULL,
  activo BOOLEAN DEFAULT TRUE,
  id_persona INT NOT NULL,
  id_rol INT NOT NULL,

  FOREIGN KEY (id_persona)
    REFERENCES persona(id_persona)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_rol)
    REFERENCES rol(id_rol)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE menu (
  id_menu INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  ruta VARCHAR(255),
  id_menu_padre INT,

  FOREIGN KEY (id_menu_padre)
    REFERENCES menu(id_menu)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

CREATE TABLE rol_menu (
  id_rol INT,
  id_menu INT,

  PRIMARY KEY (id_rol, id_menu),

  FOREIGN KEY (id_rol)
    REFERENCES rol(id_rol)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_menu)
    REFERENCES menu(id_menu)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- BLOQUE 2: OFERTA ACADÉMICA

CREATE TABLE programa_academico (
  id_programa INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  nivel VARCHAR(50) COMMENT 'PREGRADO | POSGRADO | TECNICO',
  activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE pensum (
  id_pensum INT AUTO_INCREMENT PRIMARY KEY,
  id_programa INT NOT NULL,
  version VARCHAR(20) NOT NULL COMMENT 'Ej: 2018, 2022-A',
  total_semestres INT NOT NULL,
  fecha_vigencia DATE NOT NULL,
  activo BOOLEAN DEFAULT TRUE,

  UNIQUE (id_programa, version),

  FOREIGN KEY (id_programa)
    REFERENCES programa_academico(id_programa)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE asignatura (
  id_asignatura INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  creditos INT NOT NULL
);

CREATE TABLE pensum_asignatura (
  id_pensum INT NOT NULL,
  id_asignatura INT NOT NULL,
  semestre INT NOT NULL,
  obligatoria BOOLEAN NOT NULL DEFAULT TRUE,

  PRIMARY KEY (id_pensum, id_asignatura),

  FOREIGN KEY (id_pensum)
    REFERENCES pensum(id_pensum)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_asignatura)
    REFERENCES asignatura(id_asignatura)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE prerequisito (
  id_pensum INT NOT NULL,
  id_asignatura INT NOT NULL,
  id_prerequisito INT NOT NULL,

  PRIMARY KEY (id_pensum, id_asignatura, id_prerequisito),

  FOREIGN KEY (id_pensum)
    REFERENCES pensum(id_pensum)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_asignatura)
    REFERENCES asignatura(id_asignatura)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_prerequisito)
    REFERENCES asignatura(id_asignatura)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE periodo_academico (
  id_periodo INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(255),
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  activo BOOLEAN DEFAULT TRUE
);

-- BLOQUE 3: COBRO

CREATE TABLE regla_cobro (
  id_regla INT AUTO_INCREMENT PRIMARY KEY,
  modalidad VARCHAR(50) NOT NULL COMMENT 'GLOBAL | POR_CREDITOS',
  valor DECIMAL(10,2) NOT NULL,
  id_periodo INT NOT NULL,
  id_programa INT NOT NULL,

  UNIQUE (id_periodo, id_programa, modalidad),

  FOREIGN KEY (id_periodo)
    REFERENCES periodo_academico(id_periodo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_programa)
    REFERENCES programa_academico(id_programa)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE estudiante (
  id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
  codigo_estudiantil VARCHAR(50) NOT NULL UNIQUE,
  documento_identidad VARCHAR(50) NOT NULL UNIQUE,
  primer_nombre VARCHAR(50) NOT NULL,
  segundo_nombre VARCHAR(50),
  apellido VARCHAR(50) NOT NULL,
  segundo_apellido VARCHAR(50),
  correo VARCHAR(100),
  telefono VARCHAR(20),
  activo BOOLEAN DEFAULT TRUE,
  id_programa INT NOT NULL,
  id_pensum INT NOT NULL,

  FOREIGN KEY (id_programa)
    REFERENCES programa_academico(id_programa)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_pensum)
    REFERENCES pensum(id_pensum)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE inscripcion (
  id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
  modalidad_cobro VARCHAR(50) NOT NULL COMMENT 'GLOBAL | POR_CREDITOS',
  semestre_a_cursar INT NOT NULL,
  fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
  id_estudiante INT NOT NULL,
  id_programa INT NOT NULL,
  id_pensum INT NOT NULL,
  id_periodo INT NOT NULL,

  UNIQUE (id_estudiante, id_periodo),

  FOREIGN KEY (id_estudiante)
    REFERENCES estudiante(id_estudiante)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_programa)
    REFERENCES programa_academico(id_programa)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_pensum)
    REFERENCES pensum(id_pensum)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_periodo)
    REFERENCES periodo_academico(id_periodo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE inscripcion_asignatura (
  id_inscripcion INT NOT NULL,
  id_asignatura INT NOT NULL,
  semestre_snapshot INT NOT NULL,
  creditos_snapshot INT NOT NULL,
  prerequisitos_validados BOOLEAN NOT NULL DEFAULT FALSE,

  PRIMARY KEY (id_inscripcion, id_asignatura),

  FOREIGN KEY (id_inscripcion)
    REFERENCES inscripcion(id_inscripcion)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  FOREIGN KEY (id_asignatura)
    REFERENCES asignatura(id_asignatura)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE historial_academico (
  id_historial INT AUTO_INCREMENT PRIMARY KEY,
  id_estudiante INT NOT NULL,
  id_asignatura INT NOT NULL,
  id_periodo INT NOT NULL,
  nota_final DECIMAL(5,2),
  estado VARCHAR(50) NOT NULL COMMENT 'APROBADA | REPROBADA | EN_CURSO | CANCELADA',
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,

  UNIQUE (id_estudiante, id_asignatura, id_periodo),

  FOREIGN KEY (id_estudiante)
    REFERENCES estudiante(id_estudiante)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_asignatura)
    REFERENCES asignatura(id_asignatura)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_periodo)
    REFERENCES periodo_academico(id_periodo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- BLOQUE 4: CONTABILIDAD

CREATE TABLE codigo_detalle (
  id_codigo INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(255) NOT NULL,
  grupo VARCHAR(50) NOT NULL COMMENT 'COBRO | PAGO'
);

CREATE TABLE cuenta_corriente (
  id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
  monto DECIMAL(10,2) NOT NULL,
  tipo VARCHAR(50) NOT NULL COMMENT 'COBRO | PAGO',
  fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
  descripcion_breve VARCHAR(255),
  origen VARCHAR(50) COMMENT 'INDIVIDUAL | MASIVO | CAJA | EN_LINEA',

  id_estudiante INT NOT NULL,
  id_periodo INT NOT NULL,
  id_codigo_detalle INT NOT NULL,
  id_inscripcion INT NOT NULL,

  FOREIGN KEY (id_estudiante)
    REFERENCES estudiante(id_estudiante)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_periodo)
    REFERENCES periodo_academico(id_periodo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_codigo_detalle)
    REFERENCES codigo_detalle(id_codigo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  FOREIGN KEY (id_inscripcion)
    REFERENCES inscripcion(id_inscripcion)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);





