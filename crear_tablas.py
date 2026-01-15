import os
import psycopg2
from dotenv import load_dotenv

# 1. Cargar las credenciales
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("❌ ERROR: No se encontró DATABASE_URL en el archivo .env")
    exit()

# 2. El SQL para crear las tablas del cubo
sql_crear_tablas = """
-- Borrar si existen para empezar limpio
DROP TABLE IF EXISTS hechos_citas CASCADE;
DROP TABLE IF EXISTS dim_medico CASCADE;
DROP TABLE IF EXISTS dim_paciente CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;

-- 1. Dimensión TIEMPO
CREATE TABLE dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    fecha_completa DATE UNIQUE,
    anio INT,
    mes INT,
    nombre_mes VARCHAR(20),
    dia INT,
    dia_semana VARCHAR(20)
);

-- 2. Dimensión MÉDICO
CREATE TABLE dim_medico (
    id_medico_dw SERIAL PRIMARY KEY,
    id_medico_real INT UNIQUE, 
    nombre_completo VARCHAR(150),
    especialidad VARCHAR(100)
);

-- 3. Dimensión PACIENTE
CREATE TABLE dim_paciente (
    id_paciente_dw SERIAL PRIMARY KEY,
    id_paciente_real INT UNIQUE, 
    rango_edad VARCHAR(50)
);

-- 4. TABLA DE HECHOS (Las Citas)
CREATE TABLE hechos_citas (
    id_hecho SERIAL PRIMARY KEY,
    id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
    id_medico INT REFERENCES dim_medico(id_medico_dw),
    id_paciente INT REFERENCES dim_paciente(id_paciente_dw),
    cantidad INT DEFAULT 1,
    ingreso_estimado DECIMAL(10,2) DEFAULT 500.00
);
"""

# 3. Conectarse y Ejecutar
try:
    print("🔌 Conectando a la base de datos...")
    conn = psycopg2.connect(DB_URL, sslmode='require')
    cur = conn.cursor()
    
    print("🔨 Creando tablas del cubo...")
    cur.execute(sql_crear_tablas)
    
    conn.commit()
    conn.close()
    print("✅ ¡Tablas creadas con éxito! Ahora ya puedes correr el ETL.")

except Exception as e:
    print(f"❌ Error: {e}")