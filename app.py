import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'  # Cambia esto por algo aleatorio

# 1. CONFIGURACIÓN DE LA BASE DE DATOS
# Render busca esta variable de entorno automáticamente.
# Si estás en local, asegúrate de tener tu .env configurado.
DB_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

# ==============================================================================
# RUTA DE INICIO Y LOGIN
# ==============================================================================
@app.route('/',methods=['GET', 'POST'])
def index():
    # Si ya inició sesión, lo mandamos a su portal correspondiente
    if 'rol' in session:
        if session['rol'] == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif session['rol'] == 'medico':
            return redirect(url_for('dashboard_medico'))
        elif session['rol'] == 'paciente':
            return redirect(url_for('dashboard_paciente'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Buscamos en la tabla usuarios_web
    cur.execute("""
        SELECT id, nombre_usuario, rol, id_medico, id_paciente, fullname 
        FROM usuarios_web 
        WHERE nombre_usuario = %s AND contraseña = %s
    """, (usuario, password))
    
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        # Guardamos datos en la sesión (Cookies del navegador)
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['rol'] = user[2]
        session['id_medico'] = user[3]
        session['id_paciente'] = user[4]
        session['fullname'] = user[5]

        # Redirección según el Rol
        if session['rol'] == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif session['rol'] == 'medico':
            return redirect(url_for('dashboard_medico'))
        elif session['rol'] == 'paciente':
            return redirect(url_for('dashboard_paciente'))
    else:
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

# ==============================================================================
# PORTAL 1: ADMINISTRADOR (Ve todo y Registra todo)
# ==============================================================================
@app.route('/portal_admin')
def dashboard_admin():
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Obtener lista de Médicos
    cur.execute("SELECT * FROM MEDICO ORDER BY id_medico")
    medicos = cur.fetchall()

    # 2. Obtener lista de Pacientes
    cur.execute("SELECT * FROM PACIENTE ORDER BY id_paciente")
    pacientes = cur.fetchall()

    # 3. Obtener TODAS las citas (Reporte General)
    cur.execute("""
        SELECT C.fecha_hora, 
               P.nombre_pila || ' ' || P.apellido_paterno AS paciente,
               M.nombre_pila || ' ' || M.apellido_paterno AS medico,
               C.motivo
        FROM CITA C
        JOIN PACIENTE P ON C.id_paciente = P.id_paciente
        JOIN MEDICO M ON C.id_medico = M.id_medico
        ORDER BY C.fecha_hora DESC
    """)
    todas_citas = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin_home.html', medicos=medicos, pacientes=pacientes, citas=todas_citas)

# --- ACCIONES DEL ADMIN: REGISTRAR ---

@app.route('/guardar_medico', methods=['POST'])
def guardar_medico():
    if session.get('rol') != 'admin': return redirect(url_for('index'))
    
    nombre = request.form['nombre']
    paterno = request.form['paterno']
    materno = request.form['materno']
    especialidad = request.form['especialidad']
    user_login = request.form['usuario_login']
    pass_login = request.form['password_login']

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Crear Médico
        cur.execute("""
            INSERT INTO MEDICO (nombre_pila, apellido_paterno, apellido_materno, especialidad)
            VALUES (%s, %s, %s, %s) RETURNING id_medico
        """, (nombre, paterno, materno, especialidad))
        new_id = cur.fetchone()[0]

        # 2. Crear Usuario Login
        cur.execute("""
            INSERT INTO usuarios_web (nombre_usuario, contraseña, fullname, rol, id_medico)
            VALUES (%s, %s, %s, 'medico', %s)
        """, (user_login, pass_login, f"Dr. {nombre} {paterno}", new_id))
        
        conn.commit()
        flash('Médico registrado exitosamente', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar médico: {e}', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('dashboard_admin'))

@app.route('/guardar_paciente', methods=['POST'])
def guardar_paciente():
    # Permitimos que el admin registre, o podrías abrir esta ruta al público para registrarse solo
    if request.method == 'POST':
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        nacimiento = request.form['nacimiento']
        user_login = request.form['usuario_login']
        pass_login = request.form['password_login']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # 1. Crear Paciente
            cur.execute("""
                INSERT INTO PACIENTE (nombre_pila, apellido_paterno, apellido_materno, fecha_nacimiento)
                VALUES (%s, %s, %s, %s) RETURNING id_paciente
            """, (nombre, paterno, materno, nacimiento))
            new_id = cur.fetchone()[0]

            # 2. Crear Usuario Login
            cur.execute("""
                INSERT INTO usuarios_web (nombre_usuario, contraseña, fullname, rol, id_paciente)
                VALUES (%s, %s, %s, 'paciente', %s)
            """, (user_login, pass_login, f"{nombre} {paterno}", new_id))
            
            conn.commit()
            flash('Paciente registrado exitosamente', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar paciente: {e}', 'error')
        finally:
            cur.close()
            conn.close()
            
        # Si lo registró el admin, vuelve al admin. Si fue registro público, al login.
        if session.get('rol') == 'admin':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('index'))

# ==============================================================================
# PORTAL 2: MÉDICO (Solo ve SU agenda)
# ==============================================================================
@app.route('/portal_medico')
def dashboard_medico():
    if 'rol' not in session or session['rol'] != 'medico':
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Traer citas filtradas por el ID del médico logueado
    cur.execute("""
        SELECT C.fecha_hora, 
               P.nombre_pila || ' ' || P.apellido_paterno AS paciente,
               C.motivo
        FROM CITA C
        JOIN PACIENTE P ON C.id_paciente = P.id_paciente
        WHERE C.id_medico = %s
        ORDER BY C.fecha_hora ASC
    """, (session['id_medico'],))
    
    mi_agenda = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('medico_home.html', citas=mi_agenda)

# ==============================================================================
# PORTAL 3: PACIENTE (Ve sus citas y AGENDA nuevas)
# ==============================================================================
@app.route('/portal_paciente')
def dashboard_paciente():
    if 'rol' not in session or session['rol'] != 'paciente':
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Ver MIS citas anteriores
    cur.execute("""
        SELECT C.fecha_hora, 
               M.nombre_pila || ' ' || M.apellido_paterno AS medico, 
               M.especialidad, 
               C.motivo
        FROM CITA C
        JOIN MEDICO M ON C.id_medico = M.id_medico
        WHERE C.id_paciente = %s
        ORDER BY C.fecha_hora DESC
    """, (session['id_paciente'],))
    mis_citas = cur.fetchall()

    # 2. Traer lista de Médicos (Para llenar el "Select" del formulario de nueva cita)
    cur.execute("SELECT id_medico, nombre_pila, apellido_paterno, especialidad FROM MEDICO")
    lista_medicos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('paciente_home.html', citas=mis_citas, medicos=lista_medicos)

# --- ACCIÓN PRINCIPAL: AGENDAR CITA (CON VALIDACIÓN DE TRASLAPE) ---

@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    if 'rol' not in session: return redirect(url_for('index'))

    # Si es paciente, tomamos su ID de la sesión. Si es admin, del formulario.
    if session['rol'] == 'paciente':
        id_paciente = session['id_paciente']
    else:
        id_paciente = request.form.get('id_paciente')

    id_medico = request.form['id_medico']
    fecha_hora = request.form['fecha_hora']
    motivo = request.form['motivo']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Intento de inserción
        cur.execute("""
            INSERT INTO CITA (id_paciente, id_medico, fecha_hora, motivo)
            VALUES (%s, %s, %s, %s)
        """, (id_paciente, id_medico, fecha_hora, motivo))
        
        conn.commit()
        flash('¡Cita agendada exitosamente!', 'success')

    except psycopg2.errors.UniqueViolation:
        # ¡AQUÍ CAPTURAMOS EL TRASLAPE!
        conn.rollback()
        flash('⚠️ ERROR: El médico ya tiene una cita ocupada en ese horario exacto. Elige otra hora.', 'error')
    
    except Exception as e:
        conn.rollback()
        flash(f'Ocurrió un error: {e}', 'error')
    
    finally:
        cur.close()
        conn.close()

    # Retornar a la pantalla correcta
    if session['rol'] == 'paciente':
        return redirect(url_for('dashboard_paciente'))
    elif session['rol'] == 'admin':
        return redirect(url_for('dashboard_admin'))
    
    return redirect(url_for('index'))

# ==============================================================================
# PORTAL 4: CUBO DE DATOS / REPORTES BI
# ==============================================================================
@app.route('/cubo')
def cubo():
    # Verificamos que el usuario esté logueado
    if 'rol' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()

    # --- 1. KPI: Total Ingresos ---
    # Si no tienes la tabla Fact_Citas, intenta sumar de CITA (estimado)
    try:
        cur.execute("SELECT SUM(ingreso_estimado) FROM Fact_Citas")
        total_ingresos = cur.fetchone()[0] or 0
    except:
        # Fallback si no existe el cubo: Valor dummy o 0
        conn.rollback()
        total_ingresos = 0

    # --- 2. KPI: Total Citas ---
    cur.execute("SELECT COUNT(*) FROM CITA")
    total_citas = cur.fetchone()[0]

    # --- 3. Gráfico: Citas por Mes (Ejemplo usando fecha de CITA) ---
    cur.execute("""
        SELECT TO_CHAR(fecha_hora, 'Month'), COUNT(*) 
        FROM CITA 
        GROUP BY TO_CHAR(fecha_hora, 'Month')
    """)
    datos_meses = cur.fetchall()
    # Separamos en dos listas para Chart.js
    etiquetas_meses = [fila[0].strip() for fila in datos_meses] if datos_meses else []
    valores_meses = [fila[1] for fila in datos_meses] if datos_meses else []

    # --- 4. Gráfico: Citas por Especialidad ---
    cur.execute("""
        SELECT M.especialidad, COUNT(C.id_cita)
        FROM CITA C
        JOIN MEDICO M ON C.id_medico = M.id_medico
        GROUP BY M.especialidad
    """)
    datos_esp = cur.fetchall()
    etiquetas_esp = [fila[0] for fila in datos_esp] if datos_esp else []
    valores_esp = [fila[1] for fila in datos_esp] if datos_esp else []

    cur.close()
    conn.close()

    # Renderizamos la plantilla pasando todos los datos
    return render_template('cubo.html', 
        ingresos=[total_ingresos], # Pasamos como lista para sum en jinja
        conteo_citas=[total_citas],
        meses=etiquetas_meses,
        ingresos_por_mes=valores_meses, # Reutilizamos variable para el ejemplo
        especialidades=etiquetas_esp,
        citas_por_esp=valores_esp)

if __name__ == '__main__':
    app.run(debug=True)