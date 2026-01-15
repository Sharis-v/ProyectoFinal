from datetime import datetime

def calcular_rango_edad(fecha_nac):
    if not fecha_nac: return "Desconocido"
    hoy = datetime.now().date()
    # Aproximación simple de edad
    edad = hoy.year - fecha_nac.year
    
    if edad < 12: return "Niño (0-11)"
    elif edad < 18: return "Adolescente (12-17)"
    elif edad < 30: return "Joven (18-29)"
    elif edad < 60: return "Adulto (30-59)"
    else: return "Tercera Edad (60+)"

def transformar_tiempo(fecha_dt):
    # Recibe un objeto datetime
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    return (
        fecha_dt.date(),                # fecha_completa
        fecha_dt.year,                  # anio
        fecha_dt.month,                 # mes
        fecha_dt.strftime('%B'),        # nombre_mes
        fecha_dt.day,                   # dia
        dias_semana[fecha_dt.weekday()],# dia_semana
        (fecha_dt.month - 1) // 3 + 1   # trimestre
    )