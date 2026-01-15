import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# 1. Cargar las variables del archivo .env
load_dotenv() 

# 2. Obtener la URL de la base de datos (Si falla, avisa)
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("❌ Error: No se encontró la variable DATABASE_URL en el archivo .env")

def conectar():
    try:
        # sslmode='require' es obligatorio para Render
        return psycopg2.connect(DB_URL, sslmode='require')
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        return None

def ejecutar_etl():
    conn = conectar()
    if not conn:
        return # Si no hay conexión, paramos aquí
        
    cur = conn.cursor()
    
    print("🔄 Iniciando proceso ETL (Llenando el Cubo)...")

    # --- AQUÍ VA TU LÓGICA DE ETL (Mantenemos la que tenías) ---
    
    # 1. LLENAR DIMENSIÓN MÉDICO
    try:
        cur.execute("""
            INSERT INTO dim_medico (id_medico_real, nombre_completo, especialidad)
            SELECT id_medico, nombre_pila || ' ' || apellido_paterno, especialidad
            FROM MEDICO
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Médicos cargados.")

        # 2. LLENAR DIMENSIÓN PACIENTE
        cur.execute("""
            INSERT INTO dim_paciente (id_paciente_real, rango_edad)
            SELECT 
                id_paciente,
                CASE 
                    WHEN EXTRACT(YEAR FROM age(fecha_nacimiento)) < 18 THEN 'Niño/Adolescente'
                    WHEN EXTRACT(YEAR FROM age(fecha_nacimiento)) < 60 THEN 'Adulto'
                    ELSE 'Tercera Edad'
                END
            FROM PACIENTE
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Pacientes cargados.")

        # 3. PROCESAR FECHAS Y CITAS
        cur.execute("SELECT id_cita, fecha_hora, id_medico, id_paciente FROM CITA")
        citas = cur.fetchall()

        for cita in citas:
            fecha_obj = cita[1]
            
            # A. Asegurar que la fecha exista en dim_tiempo
            cur.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha_completa = %s", (fecha_obj.date(),))
            resultado_tiempo = cur.fetchone()
            
            if not resultado_tiempo:
                dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                cur.execute("""
                    INSERT INTO dim_tiempo (fecha_completa, anio, mes, nombre_mes, dia, dia_semana)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_tiempo
                """, (
                    fecha_obj.date(), 
                    fecha_obj.year, 
                    fecha_obj.month, 
                    fecha_obj.strftime('%B'), 
                    fecha_obj.day,
                    dias_semana[fecha_obj.weekday()]
                ))
                id_tiempo = cur.fetchone()[0]
            else:
                id_tiempo = resultado_tiempo[0]

            # B. Obtener IDs de las dimensiones
            cur.execute("SELECT id_medico_dw FROM dim_medico WHERE id_medico_real = %s", (cita[2],))
            id_med_dw = cur.fetchone()
            id_med_dw = id_med_dw[0] if id_med_dw else None

            cur.execute("SELECT id_paciente_dw FROM dim_paciente WHERE id_paciente_real = %s", (cita[3],))
            id_pac_dw = cur.fetchone()
            id_pac_dw = id_pac_dw[0] if id_pac_dw else None

            # C. Insertar el HECHO
            if id_med_dw and id_pac_dw:
                cur.execute("""
                    INSERT INTO hechos_citas (id_tiempo, id_medico, id_paciente, cantidad, ingreso_estimado)
                    VALUES (%s, %s, %s, 1, 500.00)
                """, (id_tiempo, id_med_dw, id_pac_dw))

        conn.commit()
        print("✨ ¡Cubo de datos actualizado con éxito!")
        
    except Exception as e:
        print(f"⚠️ Error durante la carga de datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    ejecutar_etl()