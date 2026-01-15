-- =================================================================================
-- 1. LIMPIEZA TOTAL (RESET DE FÁBRICA)
-- =================================================================================
DROP TABLE IF EXISTS CITA CASCADE;
DROP TABLE IF EXISTS HISTORIAL_CLINICO CASCADE;
DROP TABLE IF EXISTS CONTACTO_EMERGENCIA CASCADE;
DROP TABLE IF EXISTS PACIENTE_TELEFONO CASCADE;
DROP TABLE IF EXISTS PACIENTE_ASEGURADO CASCADE;
DROP TABLE IF EXISTS PACIENTE_PRIVADO CASCADE;
DROP TABLE IF EXISTS PACIENTE CASCADE;
DROP TABLE IF EXISTS MEDICO CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS usuarios_web CASCADE;

-- =================================================================================
-- 2. CREACIÓN DE TABLAS DEL CONSULTORIO
-- =================================================================================

-- 2.1 TABLA MÉDICO
CREATE TABLE MEDICO (
    id_medico SERIAL PRIMARY KEY,
    nombre_pila VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50),
    especialidad VARCHAR(100) NOT NULL,
    CONSTRAINT uq_medico_nombre_esp UNIQUE (nombre_pila, apellido_paterno, apellido_materno, especialidad)
);

-- 2.2 TABLA PACIENTE (Supertipo)
CREATE TABLE PACIENTE (
    id_paciente SERIAL PRIMARY KEY,
    nombre_pila VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50),
    fecha_nacimiento DATE CHECK (fecha_nacimiento < CURRENT_DATE),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2.3 SUBTIPOS DE PACIENTE
CREATE TABLE PACIENTE_ASEGURADO (
    id_paciente INT PRIMARY KEY,
    no_poliza VARCHAR(50) NOT NULL UNIQUE,
    aseguradora VARCHAR(100) NOT NULL,
    CONSTRAINT fk_asegurado FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE
);

CREATE TABLE PACIENTE_PRIVADO (
    id_paciente INT PRIMARY KEY,
    rfc VARCHAR(13) NOT NULL UNIQUE,
    requiere_factura BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_privado FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE
);

-- 2.4 DETALLES DEL PACIENTE
CREATE TABLE PACIENTE_TELEFONO (
    id_paciente INT,
    telefono VARCHAR(15) NOT NULL,
    PRIMARY KEY (id_paciente, telefono),
    CONSTRAINT fk_telefono FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE
);

CREATE TABLE CONTACTO_EMERGENCIA (
    id_contacto SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL,
    nombre_contacto VARCHAR(100) NOT NULL,
    telefono_contacto VARCHAR(20) NOT NULL,
    parentesco VARCHAR(50),
    CONSTRAINT fk_contacto FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE
);

CREATE TABLE HISTORIAL_CLINICO (
    id_historial SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL,
    diagnostico VARCHAR(200) NOT NULL,
    tratamiento VARCHAR(200),
    fecha DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_historial FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE
);

-- 2.5 TABLA CITA (CON PROTECCIÓN ANTI-TRASLAPES)
CREATE TABLE CITA (
    id_cita SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_medico INT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    motivo VARCHAR(255),
    CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente) ON DELETE CASCADE,
    CONSTRAINT fk_cita_medico FOREIGN KEY (id_medico) REFERENCES MEDICO(id_medico) ON DELETE RESTRICT,
    
    -- ¡ESTO ES EL CANDADO! Impide que un médico tenga dos citas a la misma hora exacta
    CONSTRAINT no_traslapes UNIQUE (id_medico, fecha_hora)
);

-- =================================================================================
-- 3. TABLA DE LOGIN Y ROLES (INTEGRADA)
-- =================================================================================
CREATE TABLE usuarios_web (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    fullname VARCHAR(100),
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin', 'medico', 'paciente')), -- Define permisos
    id_medico INT REFERENCES MEDICO(id_medico),       -- Vincula si es doctor
    id_paciente INT REFERENCES PACIENTE(id_paciente)  -- Vincula si es paciente
);

-- =================================================================================
-- 4. POBLADO DE DATOS (DATA SEEDING)
-- =================================================================================

-- 4.1 Insertar Médicos
INSERT INTO MEDICO (nombre_pila, apellido_paterno, apellido_materno, especialidad) VALUES
('Gabriel', 'Hurtado', 'Avilés', 'Medicina Interna'),  -- ID 1
('Ana', 'Hernández', 'Ruiz', 'Cardiología'),           -- ID 2
('Sofia', 'Ramirez', 'Luna', 'Pediatría');             -- ID 3

-- 4.2 Insertar Pacientes
INSERT INTO PACIENTE (nombre_pila, apellido_paterno, apellido_materno, fecha_nacimiento) VALUES
('Fernanda', 'Montiel', 'Valdivia', '1999-03-10'),     -- ID 1
('Mario', 'Torres', 'Peña', '1985-11-20'),             -- ID 2
('Carlos', 'Mendoza', 'Soto', '2015-06-15');           -- ID 3

-- 4.3 Insertar Citas (Agenda Ocupada para pruebas)
-- Dr. Gabriel (ID 1) tiene agenda el 17 de Noviembre
INSERT INTO CITA (id_paciente, id_medico, fecha_hora, motivo) VALUES
(2, 1, '2025-11-17 09:00:00', 'Chequeo General'),
(3, 1, '2025-11-17 10:00:00', 'Dolor de cabeza persistente');

-- Dra. Ana (ID 2) tiene agenda el mismo día
INSERT INTO CITA (id_paciente, id_medico, fecha_hora, motivo) VALUES
(1, 2, '2025-11-17 11:00:00', 'Revisión cardiológica anual');


-- 4.4 CREAR USUARIOS PARA EL LOGIN (¡AQUÍ ESTÁ LA MAGIA DE ROLES!)

-- USUARIO 1: ADMIN (Ve todo)
INSERT INTO usuarios_web (nombre_usuario, contraseña, fullname, rol) 
VALUES ('admin', 'admin123', 'Super Administrador', 'admin');

-- USUARIO 2: MÉDICO (Dr. Gabriel - Solo ve su agenda)
-- Está vinculado al id_medico = 1
INSERT INTO usuarios_web (nombre_usuario, contraseña, fullname, rol, id_medico) 
VALUES ('drgabriel', 'medico123', 'Dr. Gabriel Hurtado', 'medico', 1);

-- USUARIO 3: PACIENTE (Fernanda - Solo ve sus citas y puede agendar)
-- Está vinculada al id_paciente = 1
INSERT INTO usuarios_web (nombre_usuario, contraseña, fullname, rol, id_paciente) 
VALUES ('fernanda', 'paciente123', 'Fernanda Montiel', 'paciente', 1);