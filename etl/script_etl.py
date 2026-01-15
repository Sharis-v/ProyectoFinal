import psycopg2
from datetime import datetime

# === CONFIGURACIÓN ===
# Pega aquí la misma URL que usas en tu app.py (la de Render o local)
DB_URL = "postgres://usuario:password@host/nombre_base_datos" 

def conectar():
    return psycopg2.connect(DB_URL)

def ejecutar_etl():
    conn = conectar()
    cur = conn.cursor()
    
    print("🔄 Iniciando proceso ETL (Llenando el Cubo)...")

    # 1. LLENAR DIMENSIÓN MÉDICO
    # Leemos de la tabla MEDICO real y llenamos dim_medico
    cur.execute("""
        INSERT INTO dim_medico (id_medico_real, nombre_completo, especialidad)
        SELECT id_medico, nombre_pila || ' ' || apellido_paterno, especialidad
        FROM MEDICO
        ON CONFLICT DO NOTHING;
    """)
    print("✅ Médicos cargados.")

    # 2. LLENAR DIMENSIÓN PACIENTE
    # Calculamos si es niño o adulto al vuelo
    cur.execute("""
        INSERT INTO dim_paciente (id_paciente_real, rango_edad)
        SELECT 
            id_paciente,
            CASE 
                WHEN EXTRACT(YEAR FROM age(fecha_nacimiento)) < 18 THEN 'Niño/Adolescente'
                WHEN EXTRACT(YEAR FROM age(fecha_nacimiento)) < 60 THEN 'Adulto'
                ELSE 'Tercera Edad'
            END
        FROM PACIENTE;
    """)
    print("✅ Pacientes cargados.")

    # 3. PROCESAR FECHAS Y CITAS (Lo más importante)
    # Seleccionamos todas las citas
    cur.execute("SELECT id_cita, fecha_hora, id_medico, id_paciente FROM CITA")
    citas = cur.fetchall()

    for cita in citas:
        fecha_obj = cita[1] # La fecha de la cita
        
        # A. Asegurar que la fecha exista en dim_tiempo
        cur.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha_completa = %s", (fecha_obj.date(),))
        resultado_tiempo = cur.fetchone()
        
        if not resultado_tiempo:
            # Si no existe la fecha, la creamos
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

        # C. Insertar el HECHO (La venta/cita)
        if id_med_dw and id_pac_dw:
            cur.execute("""
                INSERT INTO hechos_citas (id_tiempo, id_medico, id_paciente, cantidad, ingreso_estimado)
                VALUES (%s, %s, %s, 1, 500.00)
            """, (id_tiempo, id_med_dw, id_pac_dw))

    conn.commit()
    conn.close()
    print("✨ ¡Cubo de datos actualizado con éxito!")

if __name__ == "__main__":
    ejecutar_etl()