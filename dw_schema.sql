-- ==========================================
-- ESQUEMA DEL CUBO DE DATOS (Data Warehouse)
-- ==========================================

-- 1. Dimensión TIEMPO (Para filtrar por mes, año, día)
DROP TABLE IF EXISTS dim_tiempo CASCADE;
CREATE TABLE dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    fecha_completa DATE UNIQUE,
    anio INT,
    mes INT,
    nombre_mes VARCHAR(20),
    dia INT,
    dia_semana VARCHAR(20)
);

-- 2. Dimensión MÉDICO (Para saber quién trabaja más)
DROP TABLE IF EXISTS dim_medico CASCADE;
CREATE TABLE dim_medico (
    id_medico_dw SERIAL PRIMARY KEY,
    id_medico_real INT, -- ID original del sistema
    nombre_completo VARCHAR(150),
    especialidad VARCHAR(100)
);

-- 3. Dimensión PACIENTE (Para saber quién se enferma más)
DROP TABLE IF EXISTS dim_paciente CASCADE;
CREATE TABLE dim_paciente (
    id_paciente_dw SERIAL PRIMARY KEY,
    id_paciente_real INT, -- ID original del sistema
    sexo VARCHAR(20) DEFAULT 'Desconocido', -- Si tuvieras este dato
    rango_edad VARCHAR(50) -- Ejemplo: 'Niño', 'Adulto', 'Tercera Edad'
);

-- 4. TABLA DE HECHOS (El centro del cubo: Las Citas)
DROP TABLE IF EXISTS hechos_citas CASCADE;
CREATE TABLE hechos_citas (
    id_hecho SERIAL PRIMARY KEY,
    id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
    id_medico INT REFERENCES dim_medico(id_medico_dw),
    id_paciente INT REFERENCES dim_paciente(id_paciente_dw),
    
    -- MÉTRICAS (Lo que vamos a sumar)
    cantidad INT DEFAULT 1,
    ingreso_estimado DECIMAL(10,2) DEFAULT 500.00 -- Supongamos que cada consulta cuesta $500
);