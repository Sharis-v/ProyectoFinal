import psycopg2
import os
from config import Config

def crear_tablas_dw():
    print("🔨 Conectando a la Base de Datos para crear el Cubo...")
    
    try:
        conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # El SQL para crear el esquema y las tablas
        sql_commands = """
        -- 1. Crear el esquema si no existe
        CREATE SCHEMA IF NOT EXISTS dw;

        -- 2. Borrar tablas viejas si existen (en orden correcto)
        DROP TABLE IF EXISTS dw.fact_citas CASCADE;
        DROP TABLE IF EXISTS dw.dim_paciente CASCADE;
        DROP TABLE IF EXISTS dw.dim_medico CASCADE;
        DROP TABLE IF EXISTS dw.dim_tiempo CASCADE;

        -- 3. Crear Dimensión TIEMPO
        CREATE TABLE dw.dim_tiempo (
            id_tiempo_sk SERIAL PRIMARY KEY,
            fecha_completa DATE UNIQUE,
            anio INT,
            mes INT,
            nombre_mes VARCHAR(20),
            dia INT,
            dia_semana VARCHAR(20),
            trimestre INT
        );

        -- 4. Crear Dimensión MÉDICO
        CREATE TABLE dw.dim_medico (
            id_medico_sk SERIAL PRIMARY KEY,
            id_medico_nk INT,
            nombre_completo VARCHAR(150),
            especialidad VARCHAR(100)
        );

        -- 5. Crear Dimensión PACIENTE
        CREATE TABLE dw.dim_paciente (
            id_paciente_sk SERIAL PRIMARY KEY,
            id_paciente_nk INT,
            nombre_completo VARCHAR(150),
            tipo_paciente VARCHAR(50),
            rango_edad VARCHAR(50)
        );

        -- 6. Crear Tabla de HECHOS
        CREATE TABLE dw.fact_citas (
            id_hecho SERIAL PRIMARY KEY,
            id_tiempo_sk INT REFERENCES dw.dim_tiempo(id_tiempo_sk),
            id_medico_sk INT REFERENCES dw.dim_medico(id_medico_sk),
            id_paciente_sk INT REFERENCES dw.dim_paciente(id_paciente_sk),
            cantidad INT DEFAULT 1,
            ingreso_estimado DECIMAL(10,2),
            duracion_minutos INT DEFAULT 30
        );

        -- 7. Crear Índices
        CREATE INDEX idx_fact_tiempo ON dw.fact_citas(id_tiempo_sk);
        CREATE INDEX idx_fact_medico ON dw.fact_citas(id_medico_sk);
        CREATE INDEX idx_fact_paciente ON dw.fact_citas(id_paciente_sk);
        """
        
        cur.execute(sql_commands)
        conn.commit()
        conn.close()
        print("✅ ¡ÉXITO! El esquema 'dw' y las tablas del cubo fueron creadas.")
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")

if __name__ == "__main__":
    crear_tablas_dw()