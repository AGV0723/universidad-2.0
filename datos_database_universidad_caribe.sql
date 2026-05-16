use uninorte;
-- Programa académico
INSERT INTO programa_academico (codigo, nombre, nivel)
VALUES 
('ING-SIS', 'Ingeniería de Sistemas', 'PREGRADO'),
('ADM-EMP', 'Administración de Empresas', 'PREGRADO');
SELECT * from programa_academico;
-- Pensum 
INSERT INTO pensum (id_programa, version, total_semestres, fecha_vigencia)
VALUES
(1, '2022-A', 10, '2022-01-01'),
(2, '2022-A', 8, '2022-01-01');
SELECT * from pensum;

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
('EST001', '1001', 'Juan', 'Carlos', 'Perez', 'Gomez', 'juan1@mail.com', '300000001', 1, 1),
('EST002', '1002', 'Maria', NULL, 'Lopez', 'Diaz', 'maria@mail.com', '300000002', 1, 1),
('EST003', '1003', 'Andres', 'Felipe', 'Martinez', 'Rojas', 'andres@mail.com', '300000003', 1, 1),
('EST004', '1004', 'Luisa', NULL, 'Fernandez', 'Torres', 'luisa@mail.com', '300000004', 2, 2),
('EST005', '1005', 'Carlos', 'Eduardo', 'Ramirez', 'Soto', 'carlos@mail.com', '300000005', 2, 2),
('EST006', '1006', 'Ana', NULL, 'Castro', 'Mendez', 'ana@mail.com', '300000006', 1, 1),
('EST007', '1007', 'Pedro', 'Luis', 'Vargas', 'Moreno', 'pedro@mail.com', '300000007', 1, 1),
('EST008', '1008', 'Sofia', NULL, 'Herrera', 'Pineda', 'sofia@mail.com', '300000008', 2, 2),
('EST009', '1009', 'Diego', 'Alejandro', 'Suarez', 'Reyes', 'diego@mail.com', '300000009', 1, 1),
('EST010', '1010', 'Valentina', NULL, 'Ortega', 'Navas', 'valentina@mail.com', '300000010', 2, 2);

select * from estudiante;




-- 1. SEGURIDAD

INSERT INTO rol (nombre, descripcion) VALUES
('ADMINISTRADOR', 'Acceso total'),
('SUPERVISOR', 'Control de procesos'),
('ASISTENTE', 'Apoyo operativo');

INSERT INTO persona (primer_nombre, apellido, documento_identidad, correo) VALUES
('Juan', 'Perez', '2001', 'juan@mail.com'),
('Maria', 'Lopez', '2002', 'maria@mail.com'),
('Carlos', 'Gomez', '2003', 'carlos@mail.com');

INSERT INTO usuario (username, password_hash, correo, id_persona, id_rol) VALUES
('admin', 'hash1', 'admin@mail.com', 1, 1),
('supervisor', 'hash2', 'sup@mail.com', 2, 2),
('asistente', 'hash3', 'asis@mail.com', 3, 3);

INSERT INTO menu (nombre, ruta) VALUES
('Dashboard', '/dashboard'),
('Usuarios', '/usuarios'),
('Reportes', '/reportes');

INSERT INTO rol_menu (id_rol, id_menu) VALUES
(1,1),(1,2),(1,3),
(2,1),(2,3),
(3,1);

-- 2. OFERTA ACADÉMICA
INSERT INTO programa_academico (codigo, nombre, nivel) VALUES
('ING-SIS', 'Ingeniería de Sistemas', 'PREGRADO'),
('ADM-EMP', 'Administración', 'PREGRADO');

INSERT INTO pensum (id_programa, version, total_semestres, fecha_vigencia) VALUES
(1, '2022-A', 10, '2022-01-01'),
(2, '2022-A', 8, '2022-01-01');

INSERT INTO asignatura (codigo, nombre, creditos) VALUES
('MAT101', 'Matemáticas I', 3),
('PRO101', 'Programación I', 4),
('ADM101', 'Fundamentos Administración', 3);

INSERT INTO pensum_asignatura VALUES
(1,1,1,TRUE),
(1,2,1,TRUE),
(2,3,1,TRUE);

INSERT INTO prerequisito VALUES
(1,2,1); -- Programación I requiere Matemáticas I

INSERT INTO periodo_academico (codigo, descripcion, fecha_inicio, fecha_fin) VALUES
('2024-1', 'Primer semestre 2024', '2024-01-01', '2024-06-30');

-- 3. COBRO

INSERT INTO regla_cobro (modalidad, valor, id_periodo, id_programa) VALUES
('GLOBAL', 2000000, 1, 1),
('POR_CREDITOS', 150000, 1, 1),
('GLOBAL', 1800000, 1, 2);

INSERT INTO estudiante (
  codigo_estudiantil, documento_identidad, primer_nombre, apellido,
  id_programa, id_pensum
) VALUES
('EST01','3001','Ana','Torres',1,1),
('EST02','3002','Luis','Martinez',1,1),
('EST03','3003','Sofia','Rios',2,2);

INSERT INTO inscripcion (
  modalidad_cobro, semestre_a_cursar, id_estudiante, id_programa, id_pensum, id_periodo
) VALUES
('GLOBAL',1,1,1,1,1),
('POR_CREDITOS',1,2,1,1,1),
('GLOBAL',1,3,2,2,1);

INSERT INTO inscripcion_asignatura VALUES
(1,1,1,3,TRUE),
(1,2,1,4,TRUE),
(2,1,1,3,TRUE);

INSERT INTO historial_academico (
  id_estudiante, id_asignatura, id_periodo, nota_final, estado
) VALUES
(1,1,1,4.5,'APROBADA'),
(2,1,1,3.0,'APROBADA');

-- 4. CONTABILIDAD

INSERT INTO codigo_detalle (codigo, descripcion, grupo) VALUES
('MAT', 'Matrícula', 'COBRO'),
('PAG', 'Pago estudiante', 'PAGO');

INSERT INTO cuenta_corriente (
  monto, tipo, descripcion_breve, origen,
  id_estudiante, id_periodo, id_codigo_detalle, id_inscripcion
) VALUES
(2000000,'COBRO','Matrícula semestre','INDIVIDUAL',1,1,1,1),
(2000000,'PAGO','Pago completo','CAJA',1,1,2,1);