-- =========================================================
-- SCRIPT TRANSACCIONAL (T-SQL) PARA SQL SERVER 2022
-- Proyecto: Consultorio Médico
-- =========================================================

USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'ConsultorioDW')
BEGIN
    CREATE DATABASE ConsultorioDW;
END
GO

USE ConsultorioDW;
GO

-- 1. DIMENSIÓN TIEMPO
CREATE TABLE Dim_Tiempo (
    id_tiempo_sk INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INT,
    mes INT,
    nombre_mes NVARCHAR(20),
    dia INT,
    trimestre INT
);
GO

-- 2. DIMENSIÓN MÉDICO
CREATE TABLE Dim_Medico (
    id_medico_sk INT IDENTITY(1,1) PRIMARY KEY,
    id_medico_nk INT,
    nombre_completo NVARCHAR(150),
    especialidad NVARCHAR(100)
);
GO

-- 3. DIMENSIÓN PACIENTE
CREATE TABLE Dim_Paciente (
    id_paciente_sk INT IDENTITY(1,1) PRIMARY KEY,
    id_paciente_nk INT,
    tipo_paciente NVARCHAR(50), -- 'Asegurado' o 'Privado'
    rango_edad NVARCHAR(50)
);
GO

-- 4. TABLA DE HECHOS (FACT)
CREATE TABLE Fact_Citas (
    id_hecho INT IDENTITY(1,1) PRIMARY KEY,
    id_tiempo_sk INT FOREIGN KEY REFERENCES Dim_Tiempo(id_tiempo_sk),
    id_medico_sk INT FOREIGN KEY REFERENCES Dim_Medico(id_medico_sk),
    id_paciente_sk INT FOREIGN KEY REFERENCES Dim_Paciente(id_paciente_sk),
    
    -- Métricas
    cantidad_citas INT,
    ingreso_estimado DECIMAL(10,2),
    duracion_minutos INT
);
GO