from etl import transform

def cargar_medicos(conn, medicos):
    cur = conn.cursor()
    for m in medicos:
        # m = (id, nombre, apellido, especialidad)
        nombre_completo = f"{m[1]} {m[2]}"
        cur.execute("""
            INSERT INTO dw.dim_medico (id_medico_nk, nombre_completo, especialidad)
            VALUES (%s, %s, %s)
        """, (m[0], nombre_completo, m[3]))
    conn.commit()
    cur.close()

def cargar_pacientes(conn, pacientes):
    cur = conn.cursor()
    for p in pacientes:
        # p = (id, nombre, apellido, fecha_nac, tipo)
        nombre_completo = f"{p[1]} {p[2]}"
        rango = transform.calcular_rango_edad(p[3])
        
        cur.execute("""
            INSERT INTO dw.dim_paciente (id_paciente_nk, nombre_completo, tipo_paciente, rango_edad)
            VALUES (%s, %s, %s, %s)
        """, (p[0], nombre_completo, p[4], rango))
    conn.commit()
    cur.close()

def cargar_tiempo(conn, citas):
    # Extraemos todas las fechas únicas de las citas para crear la dimensión tiempo
    cur = conn.cursor()
    fechas_vistas = set()
    
    for c in citas:
        fecha_obj = c[1] # datetime de la cita
        fecha_date = fecha_obj.date()
        
        if fecha_date not in fechas_vistas:
            datos_tiempo = transform.transformar_tiempo(fecha_obj)
            cur.execute("""
                INSERT INTO dw.dim_tiempo (fecha_completa, anio, mes, nombre_mes, dia, dia_semana, trimestre)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fecha_completa) DO NOTHING
            """, datos_tiempo)
            fechas_vistas.add(fecha_date)
            
    conn.commit()
    cur.close()