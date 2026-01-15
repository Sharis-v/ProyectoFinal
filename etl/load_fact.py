import random

def cargar_hechos(conn, citas):
    cur = conn.cursor()
    
    for c in citas:
        # c = (id_cita, fecha_hora, id_medico, id_paciente)
        fecha_cita = c[1].date()
        id_medico_real = c[2]
        id_paciente_real = c[3]
        
        # 1. Buscar los ID generados (Surrogate Keys) en el DW
        cur.execute("SELECT id_tiempo_sk FROM dw.dim_tiempo WHERE fecha_completa = %s", (fecha_cita,))
        tiempo_sk = cur.fetchone()
        
        cur.execute("SELECT id_medico_sk FROM dw.dim_medico WHERE id_medico_nk = %s", (id_medico_real,))
        medico_sk = cur.fetchone()
        
        cur.execute("SELECT id_paciente_sk FROM dw.dim_paciente WHERE id_paciente_nk = %s", (id_paciente_real,))
        paciente_sk = cur.fetchone()
        
        # 2. Si todo existe, insertamos el hecho
        if tiempo_sk and medico_sk and paciente_sk:
            # Simulamos datos de negocio: Precio entre $300 y $800, Duración 20-60 min
            precio = random.choice([300, 450, 500, 600, 800])
            duracion = random.randint(20, 60)
            
            cur.execute("""
                INSERT INTO dw.fact_citas 
                (id_tiempo_sk, id_medico_sk, id_paciente_sk, cantidad, ingreso_estimado, duracion_minutos)
                VALUES (%s, %s, %s, 1, %s, %s)
            """, (tiempo_sk[0], medico_sk[0], paciente_sk[0], precio, duracion))
            
    conn.commit()
    cur.close()