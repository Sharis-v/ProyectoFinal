import psycopg2

def extraer_datos(conn):
    cur = conn.cursor()
    
    print("   ... Extrayendo Médicos")
    cur.execute("SELECT id_medico, nombre_pila, apellido_paterno, especialidad FROM MEDICO")
    medicos = cur.fetchall()
    
    print("   ... Extrayendo Pacientes (Detectando tipo)")
    # Hacemos un LEFT JOIN para ver si existe en la tabla de asegurados
    cur.execute("""
        SELECT 
            p.id_paciente, 
            p.nombre_pila, 
            p.apellido_paterno, 
            p.fecha_nacimiento,
            CASE WHEN pa.no_poliza IS NOT NULL THEN 'Asegurado' ELSE 'Privado' END as tipo
        FROM PACIENTE p
        LEFT JOIN PACIENTE_ASEGURADO pa ON p.id_paciente = pa.id_paciente
    """)
    pacientes = cur.fetchall()
    
    print("   ... Extrayendo Citas")
    cur.execute("SELECT id_cita, fecha_hora, id_medico, id_paciente FROM CITA")
    citas = cur.fetchall()
    
    cur.close()
    return medicos, pacientes, citas