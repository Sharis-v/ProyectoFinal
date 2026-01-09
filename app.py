from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno (para local)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_por_defecto_segura')

# Función para conectar a la Base de Datos (Supabase)
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# --- RUTA DE INICIO (LOGIN) ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # CONSULTA SEGURA (PRACTICA 4.1): Usamos %s para evitar SQL Injection
            # Nota: Asegúrate de tener una tabla de usuarios o usa la de médicos para probar
            # Aquí simularemos que entras si el usuario y contraseña coinciden con un médico o admin creado
            cur.execute("SELECT * FROM usuarios_web WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user:
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        else:
             flash('Error al conectar con la base de datos', 'danger')
             
    return render_template('login.html')

# --- RUTA PRINCIPAL (DASHBOARD) ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    pacientes = []
    citas = []
    
    if conn:
        cur = conn.cursor()
        
        # 1. Traer Pacientes (Tabla definida en P3/P4)
        cur.execute("SELECT id_paciente, nombre_pila, apellido_paterno, fecha_nacimiento FROM PACIENTE")
        pacientes = cur.fetchall()
        
        # 2. Traer Citas con JOIN para ver nombres de médicos y pacientes (Integración P3)
        query_citas = """
            SELECT c.fecha_hora, p.nombre_pila || ' ' || p.apellido_paterno as paciente,
                   m.nombre_pila || ' ' || m.apellido_paterno as medico, c.motivo
            FROM CITA c
            JOIN PACIENTE p ON c.id_paciente = p.id_paciente
            JOIN MEDICO m ON c.id_medico = m.id_medico
            ORDER BY c.fecha_hora ASC
        """
        cur.execute(query_citas)
        citas = cur.fetchall()
        
        cur.close()
        conn.close()

    return render_template('dashboard.html', pacientes=pacientes, citas=citas)

# --- CERRAR SESIÓN ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)