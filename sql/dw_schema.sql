-- =================================================================================
-- 1. CREACIÓN DEL ESQUEMA DW (Data Warehouse)
--    Separamos las tablas del análisis de las tablas operativas
-- =================================================================================
CREATE SCHEMA IF NOT EXISTS dw;

-- Limpieza previa si se vuelve a correr el script
DROP TABLE IF EXISTS dw.fact_citas CASCADE;
DROP TABLE IF EXISTS dw.dim_paciente CASCADE;
DROP TABLE IF EXISTS dw.dim_medico CASCADE;
DROP TABLE IF EXISTS dw.dim_tiempo CASCADE;

-- =================================================================================
-- 2. TABLAS DE DIMENSIONES (Los "Por qué", "Quién", "Cuándo")
-- =================================================================================

-- 2.1 Dimensión TIEMPO
-- Desglosamos la fecha de la cita para poder filtrar por año, mes, trimestre.
CREATE TABLE dw.dim_tiempo (
    id_tiempo_sk SERIAL PRIMARY KEY,  -- Surrogate Key (Clave artificial)
    fecha_completa DATE UNIQUE,       -- Fecha real (2025-11-17)
    anio INT,                         -- 2025
    mes INT,                          -- 11
    nombre_mes VARCHAR(20),           -- 'Noviembre'
    dia INT,                          -- 17
    dia_semana VARCHAR(20),           -- 'Lunes'
    trimestre INT                     -- 4
);

-- 2.2 Dimensión MÉDICO
-- Simplificamos la información del médico para el reporte.
CREATE TABLE dw.dim_medico (
    id_medico_sk SERIAL PRIMARY KEY,
    id_medico_nk INT,                 -- ID original de la tabla MEDICO (Natural Key)
    nombre_completo VARCHAR(150),     -- Concatenamos nombre + apellidos
    especialidad VARCHAR(100)
);

-- 2.3 Dimensión PACIENTE
-- Aquí aplicamos lógica de negocio: Calculamos si es 'Asegurado' o 'Privado' y su rango de edad.
CREATE TABLE dw.dim_paciente (
    id_paciente_sk SERIAL PRIMARY KEY,
    id_paciente_nk INT,               -- ID original de la tabla PACIENTE
    nombre_completo VARCHAR(150),
    tipo_paciente VARCHAR(50),        -- Lógica: ¿Está en tabla ASEGURADO o PRIVADO?
    rango_edad VARCHAR(50)            -- Lógica: 'Niño', 'Joven', 'Adulto', 'Tercera Edad'
);

-- =================================================================================
-- 3. TABLA DE HECHOS (El centro de la estrella)
--    Aquí registramos los eventos numéricos (las Citas)
-- =================================================================================

CREATE TABLE dw.fact_citas (
    id_hecho SERIAL PRIMARY KEY,
    
    -- Relaciones con las dimensiones (Foreign Keys)
    id_tiempo_sk INT REFERENCES dw.dim_tiempo(id_tiempo_sk),
    id_medico_sk INT REFERENCES dw.dim_medico(id_medico_sk),
    id_paciente_sk INT REFERENCES dw.dim_paciente(id_paciente_sk),
    
    -- MÉTRICAS (Lo que vamos a sumar o contar en los gráficos)
    cantidad INT DEFAULT 1,           -- Siempre 1, para hacer COUNT() de citas
    ingreso_estimado DECIMAL(10,2),   -- Simularemos un costo por consulta (ej. $500)
    duracion_minutos INT DEFAULT 30   -- Simularemos una duración promedio
);

-- Índices para mejorar la velocidad de las consultas del Cubo
CREATE INDEX idx_fact_tiempo ON dw.fact_citas(id_tiempo_sk);
CREATE INDEX idx_fact_medico ON dw.fact_citas(id_medico_sk);
CREATE INDEX idx_fact_paciente ON dw.fact_citas(id_paciente_sk);