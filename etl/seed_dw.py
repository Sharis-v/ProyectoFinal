import psycopg2
import os
import sys

# Truco para importar config desde la carpeta superior
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Importamos nuestros módulos ETL
import extract
import transform
import load_dimensions
import load_fact

def run():
    print("🚀 INICIANDO ETL DEL CONSULTORIO...")
    
    try:
        conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        
        # 1. Limpiar DW (Reset)
        print("🧹 Limpiando Data Warehouse...")
        cur.execute("TRUNCATE TABLE dw.fact_citas, dw.dim_medico, dw.dim_paciente, dw.dim_tiempo RESTART IDENTITY CASCADE;")
        conn.commit()
        
        # 2. Extract
        print("📥 Paso 1: Extracción...")
        medicos, pacientes, citas = extract.extraer_datos(conn)
        
        # 3. Load Dimensions (Transform implícito)
        print("🔄 Paso 2: Cargando Dimensiones...")
        load_dimensions.cargar_medicos(conn, medicos)
        load_dimensions.cargar_pacientes(conn, pacientes)
        load_dimensions.cargar_tiempo(conn, citas)
        
        # 4. Load Facts
        print("📊 Paso 3: Cargando Tabla de Hechos...")
        load_fact.cargar_hechos(conn, citas)
        
        conn.close()
        print("✅ ¡ÉXITO! El Cubo de Datos ha sido actualizado.")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    run()