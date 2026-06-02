use uninorte;

-- 1. ingreso de usuarios, menús y asignacion de menú a cada rol (SEGURIDAD)
INSERT INTO rol (nombre, descripcion) VALUES
('ADMINISTRADOR', 'Acceso total'),
('SUPERVISOR', 'Control de procesos'),
('ASISTENTE', 'Apoyo operativo'),
('ESTUDIANTE', 'Acceso a portal de pagos y consulta de cuenta');

INSERT INTO persona (primer_nombre, apellido, documento_identidad, correo) VALUES
('Ornulfo', 'Perez', '0123456789', 'ornulfo@mail.com'),
('Magnolia', 'Barrios', '5263148752', 'magnolia@mail.com'),
('Carlos', 'Gomez', '6784521307', 'carlos@mail.com');

 INSERT INTO usuario (username, password_hash, correo, id_persona, id_rol) VALUES
 ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin@mail.com', 1, 1), -- admin / admin
 ('supervisor', '0834c2d60725ac5902257b3b78dd161ad26d1c0290dbf1e47cc14add5b8c8142', 'sup@mail.com', 2, 2), -- supervisor / supervisor  
 ('asistente', '2b302f3e9adcbb7159bf54d4035260e5df49effedb1d56f670837efb25a46e5a', 'asis@mail.com', 3, 3); -- asistente / asistente

 INSERT INTO menu (nombre, ruta) VALUES
('Dashboard', '/dashboard'),
('Usuarios', '/usuarios'),
('Reportes', '/reportes'),
('Portal de Pagos', '/portal-pagos');

INSERT INTO rol_menu (id_rol, id_menu) VALUES
(1,1),(1,2),(1,3),
(2,1),(2,3),
(3,1),
(4,4);

-- 2. ingreso de oferta academica (asignaturas)

INSERT INTO asignatura (codigo, nombre, creditos) VALUES
('MAT1031', 'Álgebra Lineal', 3),
('MAT1101', 'Cálculo Diferencial', 5),
('MAT1111', 'Cálculo Integral', 4),
('MAT1121', 'Cálculo Vectorial', 4),
('MAT4011', 'Ecuaciones Diferenciales', 3),
('MAT4021', 'Matemáticas Discretas', 3),
('MAT4192', 'Matemáticas Fundamentales', 4),
('MAT4263', 'Teoría de la Probabilidad', 3),
('IST0010', 'Intro. a la Ing. de Sistemas', 1),
('IST2088', 'Algoritmia y Programación I', 3),
('IST2089', 'Algoritmia y Programación II', 3),
('CAS3020', 'Competencias Comunicativas I', 3),
('CAS3030', 'Competencias Comunicativas II', 3),
('ELG1150', 'Electiva en Ciencias de la Vida', 3),
('ELG1140', 'Electiva en Historia', 3),
('IBA0022', 'Expresión Gráfica', 3),
('IEN0010', 'Intro. a la Ing. Electrónica', 1),
('FIS1023', 'Física Mecánica', 4);

INSERT INTO programa_academico (codigo, nombre, nivel) VALUES
('PINGSISTEMAS', 'Ingeniería de Sistemas', 'PREGRADO'),
('PCDATOS', 'Ciencia de Datos', 'PREGRADO'),
('PINGELECTRONICA', 'Ingeniería Electrónica', 'PREGRADO');

INSERT INTO pensum (id_programa, version, total_semestres, fecha_vigencia) VALUES
(1, '2022-A', 10, '2022-01-01'),
(2, '2022-A', 8, '2022-01-01'),
(3, '2022-A', 10, '2022-01-01');

INSERT INTO pensum_asignatura (id_pensum, id_asignatura, semestre, obligatoria) VALUES -- relación pensum - asignatura
-- pensum 1 2022-A de ing de sistemas (1er semestre)
(1,1,1,TRUE), -- algebra
(1,2,1,TRUE), -- calculo 1
(1,9,1,TRUE), -- introduccion sistemas
(1,10,1,TRUE), -- algoritmia 1
(1,12,1,TRUE), -- competencias comunicativas 1
-- pensum 1 2022-A de ing de sistemas (2do semestre)
(1,15,2,TRUE), -- electiva en historia
(1,3,2,TRUE), -- calculo 1I
(1,18,2,TRUE), -- fisica mecanica
(1,11,2,TRUE), -- algoritmia 1I
(1,13,2,TRUE), -- competencias comunicativas 1I
-- pensum 2 2022-A de ciencia de datos (1er semestre)
(2,2,1,TRUE),
(2,7,1,TRUE),
(2,10,1,TRUE),
(2,12,1,TRUE),
(2,14,1,TRUE),
-- pensum 3 2022-A de ing eletronica (1er semestre)
(3,1,1,TRUE),
(3,2,1,TRUE),
(3,16,1,TRUE),
(3,17,1,TRUE),
(3,12,1,TRUE);

SELECT id_asignatura, codigo, nombre FROM asignatura ORDER BY id_asignatura;

INSERT INTO prerequisito (id_pensum, id_asignatura, id_prerequisito) VALUES
-- pensum 1 2022-A de ing de sistemas (2do semestre)
(1,3,2), -- calculo 2 tiene como prerequisito calculo 1
(1,18,2), -- fisica mecanica tiene como prerequisito calculo 1
(1,11,10), -- algoritmia 2 tiene como prerequisito algoritmia 1
(1,13,12); -- competencias comunicativas 2 tiene como prerequisito competencias comunicativas 1

INSERT INTO periodo_academico (codigo, descripcion, fecha_inicio, fecha_fin) VALUES
('202210', 'Primer semestre 2022', '2022-01-01', '2022-06-15'),
('202230', 'Segundo semestre 2022', '2022-08-01', '2022-12-10');

-- 3. COBRO

INSERT INTO regla_cobro (modalidad, valor, id_periodo, id_programa) VALUES
-- reglas de cobro ing de sistemas 2022
('GLOBAL', 13574400, 1, 1),
('POR_CREDITOS', 938000, 1, 1),
('GLOBAL', 13574400, 2, 1),
('POR_CREDITOS', 938000, 2, 1),
-- reglas de cobro ciencia de datos 2022
('GLOBAL', 13574400, 1, 2),
('POR_CREDITOS', 938000, 1, 2),
('GLOBAL', 13574400, 2, 2),
('POR_CREDITOS', 938000, 2, 2),
-- reglas de cobro ing electronica 2022
('GLOBAL', 15471900, 1, 3),
('POR_CREDITOS', 938000, 1, 3),
('GLOBAL', 15471900, 2, 3),
('POR_CREDITOS', 938000, 2, 3);

-- 4. ingreso de estudiantes (tanto en la tabla de estudiante, persona y usuario)

-- estudiantes
INSERT INTO estudiante (
  codigo_estudiantil,
  documento_identidad,
  primer_nombre,
  segundo_nombre,
  apellido,
  segundo_apellido,
  correo,
  telefono,
  id_programa,
  id_pensum
)
VALUES
('200247896', '1001111111', 'Juan', 'Carlos', 'Perez', 'Gomez', 'juan1@mail.com', '300000001', 1, 1),
('200247596', '1002222222', 'Maria', NULL, 'Lopez', 'Diaz', 'maria@mail.com', '300000002', 1, 1),
('200245687', '1003333333', 'Andres', 'Felipe', 'Martinez', 'Rojas', 'andres@mail.com', '300000003', 2, 2),
('200246510', '1004444444', 'Luisa', NULL, 'Fernandez', 'Torres', 'luisa@mail.com', '300000004', 2, 2),
('200252347', '1005555555', 'Carlos', 'Eduardo', 'Ramirez', 'Soto', 'carlos@mail.com', '300000005', 3, 3);

-- INGRESAR ESTUDIANTES A TABLA PERSONA
INSERT INTO persona (primer_nombre, apellido, documento_identidad, correo) VALUES
('Juan', 'Perez', '1001111111', 'juan1@mail.com'),
('Maria', 'Lopez', '1002222222', 'maria@mail.com'),
('Andres', 'Martinez', '1003333333', 'andres@mail.com'),
('Luisa', 'Fernandez', '1004444444', 'luisa@mail.com'),
('Carlos', 'Ramirez', '1005555555', 'carlos@mail.com');

-- INGRESAR ESTUDIANTES A TABLA USUARIO
INSERT INTO usuario (username, password_hash, correo, id_persona, id_rol) VALUES
 ('jperez', '82b084f320a2c977585ec19926d7ef45db24ad7456603a8aec434dae7400f411', 'juan1@mail.com', 4, 4),
('mlopez', '1706ac711b9f78e1be99ee5fe18d0baa99b150b50941446a80f6bc4674e3ecf2', 'maria@mail.com', 5, 4),
('amartinez', '2c5ba2413f97adf07e644bce81339ab675dd67455413707e22168dc9bef25f25', 'andres@mail.com', 6, 4),
('lfernandez', '054890b49bae7e1d15cda378bed794b3accd0f0e97f83d114c6728800f2fb911', 'luisa@mail.com', 7, 4),
('cramirez', 'a77eecf696185c76fc981d71074a02ac6e5d112cb86bd010f44a1c730cee728c', 'carlos@mail.com', 8, 4);

-- 5. CONTABILIDAD

INSERT INTO codigo_detalle (codigo, descripcion, grupo) VALUES
('PMAT', 'Valor Global por programa', 'COBRO'),
('PCRE', 'Valor crédito por programa', 'COBRO'),
('PCAR', 'Carné digital', 'COBRO'),
('PLAB', 'Laboratorios médicos', 'COBRO'),
('PEXA', 'Exámenes de ingreso', 'COBRO'),
('MPAG', 'Valor pagado para Matricula', 'PAGO'),
('ANT', 'Anticipo', 'PAGO'),
('DESC', 'Descuento', 'PAGO'),
('CRED', 'Crédito', 'PAGO');

-- 6. HISTORIAL ACADEMICO (asignaturas aprobadas en semestres anteriores), ingreso de matrículas e ingreso de datos a cuentas corrientes

INSERT INTO historial_academico (id_estudiante, id_asignatura, id_periodo, nota_final, estado) VALUES
-- estudiante 1: aprobó todas las asignaturas del semestre 1 de ing de sistemas (período 202210)
(1, 1, 1, 4.2, 'APROBADA'),   -- MAT1031 Álgebra Lineal
(1, 2, 1, 4.0, 'APROBADA'),   -- MAT1101 Cálculo Diferencial
(1, 9, 1, 4.5, 'APROBADA'),   -- IST0010 Intro. a la Ing. de Sistemas
(1, 10, 1, 3.8, 'APROBADA'),  -- IST2088 Algoritmia y Programación I
(1, 12, 1, 4.1, 'APROBADA'),  -- CAS3020 Competencias Comunicativas I

-- estudiante 2: aprobó todas las asignaturas del semestre 1 de ing de sistemas (período 202210)
(2, 1, 1, 3.9, 'APROBADA'),   -- MAT1031 Álgebra Lineal
(2, 2, 1, 4.3, 'APROBADA'),   -- MAT1101 Cálculo Diferencial
(2, 9, 1, 4.4, 'APROBADA'),   -- IST0010 Intro. a la Ing. de Sistemas
(2, 10, 1, 4.0, 'APROBADA'),  -- IST2088 Algoritmia y Programación I
(2, 12, 1, 4.2, 'APROBADA');  -- CAS3020 Competencias Comunicativas I

select * from historial_academico;

INSERT INTO inscripcion (
  modalidad_cobro, semestre_a_cursar, id_estudiante, id_programa, id_pensum, id_periodo
) VALUES
-- estudiantes de segundo semestre de ing de sistemas
('GLOBAL',2,1,1,1,1),
('GLOBAL',2,2,1,1,1),
('POR_CREDITOS',2,2,1,1,1), -- el estudiante 2 comprará 3 créditos extras para dar una asignatura más en su segundo semestre
-- estudiantes de primer semestre de ciencia de datos
('GLOBAL',1,3,2,2,1),
('GLOBAL',1,4,2,2,1),
-- estudiantes de primer semestre de ing electronica
('GLOBAL',1,5,2,3,1);

select * from inscripcion;


INSERT INTO inscripcion_asignatura (id_inscripcion, id_asignatura, semestre_snapshot, creditos_snapshot, prerequisitos_validados) VALUES
-- inscripción 1: estudiante 1 matriculado en semestre 2 de ing de sistemas (modalidad GLOBAL)
(1, 15, 2, 3, TRUE),   -- ELG1150 Electiva en Historia (no tiene prerequisitos)
(1, 3, 2, 4, TRUE),    -- MAT1111 Cálculo Integral (prerequisito: MAT1101 validado)
(1, 18, 2, 4, TRUE),   -- FIS1023 Física Mecánica (prerequisito: MAT1101 validado)
(1, 11, 2, 3, TRUE),   -- IST2089 Algoritmia y Programación II (prerequisito: IST2088 validado)
(1, 13, 2, 3, TRUE),   -- CAS3030 Competencias Comunicativas II (prerequisito: CAS3020 validado)

-- inscripción 2: estudiante 2 matriculado en semestre 2 de ing de sistemas (modalidad GLOBAL)
(2, 15, 2, 3, TRUE),   -- ELG1150 Electiva en Historia
(2, 3, 2, 4, TRUE),    -- MAT1111 Cálculo Integral
(2, 18, 2, 4, TRUE),   -- FIS1023 Física Mecánica
(2, 11, 2, 3, TRUE),   -- IST2089 Algoritmia y Programación II
(2, 13, 2, 3, TRUE),   -- CAS3030 Competencias Comunicativas II

-- inscripción 3: estudiante 2 matriculado en asignatura extra POR_CREDITOS (electiva en ciencias de la vida)
(3, 14, 2, 3, TRUE),   -- ELG1150 Electiva en Ciencias de la Vida (3 créditos)

-- inscripción 4: estudiante 3 matriculado en semestre 1 de ciencia de datos (modalidad GLOBAL)
(4, 2, 1, 5, TRUE),    -- MAT1101 Cálculo Diferencial
(4, 7, 1, 4, TRUE),    -- MAT4192 Matemáticas Fundamentales
(4, 10, 1, 3, TRUE),   -- IST2088 Algoritmia y Programación I
(4, 12, 1, 3, TRUE),   -- CAS3020 Competencias Comunicativas I
(4, 14, 1, 3, TRUE),   -- ELG1150 Electiva en Ciencias de la Vida

-- inscripción 5: estudiante 4 matriculado en semestre 1 de ciencia de datos (modalidad GLOBAL)
(5, 2, 1, 5, TRUE),    -- MAT1101 Cálculo Diferencial
(5, 7, 1, 4, TRUE),    -- MAT4192 Matemáticas Fundamentales
(5, 10, 1, 3, TRUE),   -- IST2088 Algoritmia y Programación I
(5, 12, 1, 3, TRUE),   -- CAS3020 Competencias Comunicativas I
(5, 14, 1, 3, TRUE),   -- ELG1150 Electiva en Ciencias de la Vida

-- inscripción 6: estudiante 5 matriculado en semestre 1 de ing electrónica (modalidad GLOBAL)
(6, 1, 1, 4.3, TRUE),  -- MAT1031 Álgebra Lineal
(6, 2, 1, 4.0, TRUE),  -- MAT1101 Cálculo Diferencial
(6, 16, 1, 3.9, TRUE), -- IBA0022 Expresión Gráfica
(6, 17, 1, 4.2, TRUE), -- IEN0010 Intro. a la Ing. Electrónica
(6, 12, 1, 4.1, TRUE); -- CAS3020 Competencias Comunicativas I
select * from inscripcion_asignatura;

INSERT INTO cuenta_corriente (monto, tipo, descripcion_breve, origen, id_estudiante, id_periodo, id_codigo_detalle, id_inscripcion) VALUES
-- COBROS (inscripciones de estudiantes)
-- estudiante 1: cobro de matrícula global semestre 2
(13574400, 'COBRO', 'Matrícula semestre 2 Ing Sistemas', 'INDIVIDUAL', 1, 1, 1, 1),
-- estudiante 2: cobro de matrícula global semestre 2
(13574400, 'COBRO', 'Matrícula semestre 2 Ing Sistemas', 'INDIVIDUAL', 2, 1, 1, 2),
-- estudiante 2: cobro por créditos adicionales (3 créditos × 938000 = 2,814,000)
(2814000, 'COBRO', 'Matrícula por 3 créditos electiva', 'INDIVIDUAL', 2, 1, 2, 3),
-- estudiante 3: cobro de matrícula global semestre 1
(13574400, 'COBRO', 'Matrícula semestre 1 Ciencia de Datos', 'INDIVIDUAL', 3, 1, 1, 4),
-- estudiante 4: cobro de matrícula global semestre 1
(13574400, 'COBRO', 'Matrícula semestre 1 Ciencia de Datos', 'INDIVIDUAL', 4, 1, 1, 5),
-- estudiante 5: cobro de matrícula global semestre 1
(15471900, 'COBRO', 'Matrícula semestre 1 Ing Electrónica', 'INDIVIDUAL', 5, 1, 1, 6),

-- PAGOS (simulacion de que algunos estudiantes realizan pagos)
-- estudiante 1: pago parcial del 50% de la matrícula
(6787200, 'PAGO', 'Pago parcial 50%', 'EN_LINEA', 1, 1, 1, 1),
-- estudiante 2: pago total de la matrícula
(13574400, 'PAGO', 'Pago total de matrícula', 'CAJA', 2, 1, 1, 2),
-- estudiante 3: pago de 5,000,000 a cuenta
(5000000, 'PAGO', 'Abono a cuenta', 'EN_LINEA', 3, 1, 1, 4),
-- estudiante 4: no ha pagado nada
-- estudiante 5: pago parcial del 40%
(6188760, 'PAGO', 'Pago parcial 40%', 'CAJA', 5, 1, 1, 6);

"""
use uninorte;
SET SQL_SAFE_UPDATES=0;
DELETE FROM cuenta_corriente;
DELETE FROM inscripcion_asignatura;
DELETE FROM historial_academico;
DELETE FROM inscripcion;
DELETE FROM regla_cobro;
DELETE FROM rol_menu;
DELETE FROM menu;
DELETE FROM usuario;
DELETE FROM estudiante;
DELETE FROM persona;
DELETE FROM prerequisito;
DELETE FROM pensum_asignatura;
DELETE FROM pensum;
DELETE FROM programa_academico;
DELETE FROM asignatura;
DELETE FROM periodo_academico;
DELETE FROM rol;
DELETE FROM asignatura;

ALTER TABLE rol AUTO_INCREMENT = 1;
ALTER TABLE persona AUTO_INCREMENT = 1;
ALTER TABLE usuario AUTO_INCREMENT = 1;
ALTER TABLE menu AUTO_INCREMENT = 1;
ALTER TABLE asignatura AUTO_INCREMENT = 1;
ALTER TABLE programa_academico AUTO_INCREMENT = 1;
ALTER TABLE pensum AUTO_INCREMENT = 1;
ALTER TABLE pensum_asignatura AUTO_INCREMENT = 1;
ALTER TABLE periodo_academico AUTO_INCREMENT = 1;
ALTER TABLE estudiante AUTO_INCREMENT = 1;
ALTER TABLE inscripcion AUTO_INCREMENT = 1;
ALTER TABLE regla_cobro AUTO_INCREMENT = 1;
ALTER TABLE codigo_detalle AUTO_INCREMENT = 1;
ALTER TABLE cuenta_corriente AUTO_INCREMENT = 1;

SET SQL_SAFE_UPDATES=1; 
"""