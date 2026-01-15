# 🏥 Sistema de Gestión Clínica + Inteligencia de Negocios (BI)

## 🎓 Información académica

**Institución:** INSTITUTO POLITÉCNICO NACIONAL  
**Carrera:** ESCUELA SUPERIOR DE CÓMPUTO  
**Materia:** BASES DE DATOS  
**Docente:** GABRIEL HURTADO AVILÉS  
**Semestre/Grupo:** 3CV5  
**Equipo:**
👤 Montiel Valdivia Fernanda Sharis 

---

## 📖 Resumen Ejecutivo

Este proyecto es una **aplicación web completa (End-to-End)** que integra la gestión operativa y analítica de un consultorio médico de especialidades. A través de la simulación de operaciones diarias, el sistema transforma datos transaccionales (citas y pacientes) en conocimiento estratégico.

**Componentes principales:**
* 🧱 **Sistema Transaccional (OLTP)** - Gestión de citas, expedientes y médicos en tiempo real.
* 📊 **Almacén de datos (DW)** - Repositorio histórico para análisis financiero y operativo.
* 🧊 **Cubo de Datos (OLAP)** - Operaciones analíticas multidimensionales (Ingresos, Productividad).
* 🌐 **Interfaz Web Integrada** - Visualización de KPIs y gráficos desde el mismo portal.

---

## 📑 Tabla de Contenidos

1.  [Problemática](#-1-problemática)
2.  [Objetivo del Proyecto](#-2-objetivo-del-proyecto)
3.  [Arquitectura del Sistema](#-3-arquitectura-del-sistema)
4.  [Tecnologías Utilizadas](#-4-tecnologías-utilizadas)
5.  [Estructura del Proyecto](#-5-estructura-del-proyecto)
6.  [Modelo Relacional OLTP](#-6-modelo-relacional-oltp)
7.  [Almacén de datos - Modelo Dimensional](#-7-almacén-de-datos---modelo-dimensional)
8.  [Cubo de datos OLAP](#-8-cubo-de-datos-olap)
9.  [Instalación y Ejecución](#-10-instalación-y-ejecución)
10. [Funcionalidades Implementadas](#-12-funcionalidades-implementadas)
11. [Conclusiones](#-13-conclusiones)

---

## 🛑 1. Problemática

Un centro médico de especialidades enfrentaba dos grandes desafíos:

### 🔹 Problema Operacional (OLTP)
❌ Agendas desorganizadas y empalme de horarios.  
❌ Expedientes de pacientes fragmentados o físicos.  
❌ Falta de seguridad en los datos sensibles de salud.  
❌ Inconsistencia en la información de los médicos y sus especialidades.

### 🔹 Problema Analítico (OLAP)
❌ Desconocimiento total de los ingresos reales por mes.  
❌ Imposibilidad de medir la productividad por médico.  
❌ No existían reportes históricos de afluencia de pacientes.  
❌ Falta de herramientas visuales para la toma de decisiones estratégicas.

---

## 🎯 2. Objetivo del Proyecto

Desarrollar una **plataforma integral** que permita:

### ✔ Operación Clínica (OLTP)
* **Gestión de Roles:** Portal diferenciado para Admin, Médicos y Pacientes.
* **Agenda Inteligente:** Validación automática para evitar citas traslapadas.
* **Expediente Digital:** CRUD completo de pacientes y médicos.
* **Seguridad:** Hashing de contraseñas y manejo de sesiones seguras.

### ✔ Análisis de datos (OLAP)
* Construcción de un **Data Warehouse** con esquema estrella.
* Implementación de un **Cubo OLAP Web** funcional.
* Análisis multidimensional por:
    * **Tiempo** (Mes, Año, Trimestre).
    * **Especialidad** (Cardiología, Pediatría, General).
    * **Médico** (Productividad e Ingresos generados).
* Visualización de **KPIs financieros** y gráficos interactivos.

---

## 🏗️ 3. Arquitectura del Sistema

```mermaid
graph TD
    User((Usuario)) -->|HTTPS| Web[Flask App / Gunicorn]
    Web -->|OLTP Queries| DB[(PostgreSQL - Public)]
    Web -->|OLAP Queries| DW[(PostgreSQL - DW)]
    
    subgraph "Capa de Aplicación"
        Web
        Logic[Lógica de Negocio]
        Auth[Autenticación]
    end
    
    subgraph "Capa de Datos (Supabase)"
        DB
        ETL[Proceso ETL Python]
        DW
    end
    🧱 4. Tecnologías Utilizadas
    Categoría,Tecnología,Versión,Propósito
Backend,Python (Flask),3.10+,Núcleo de la aplicación y API.
Base de Datos,PostgreSQL,15+,Motor híbrido para OLTP y OLAP (Supabase).
ORM / Driver,Psycopg2,2.9.x,Conexión optimizada a base de datos.
Frontend,Bootstrap 5 + Jinja2,v5.3,Diseño responsivo y renderizado HTML.
Visualización,Chart.js,v4.x,Gráficos interactivos en el cubo web.
Seguridad,Werkzeug,3.0.x,Hashing PBKDF2 y seguridad de sesiones.
📁 5. Estructura del Proyecto
PROYECTO_CONSULTORIO/
|
├── app.py                         # 🎮 Controlador Principal (Rutas y Lógica)
├── .env                           # 🔐 Variables de Entorno (Credenciales)
├── requirements.txt               # 📦 Dependencias Python
|
├── etl/                           # 🔄 Scripts de Transformación de Datos
│   └── seed_data.py               # Script para poblar BD inicial
|
├── static/                        # 🎨 Recursos Estáticos
│   ├── css/
│   │   ├── estilo_cubo.css        # Estilos específicos del Dashboard BI
│   │   └── style.css              # Estilos generales
│   └── img/
│       └── fondo.jpg              # Recursos gráficos
|
└── templates/                     # 📄 Vistas HTML (Jinja2)
    ├── base.html                  # Plantilla maestra (Navbar, Footer)
    ├── login.html                 # Acceso seguro
    ├── admin_home.html            # Dashboard Operativo Admin
    ├── medico_home.html           # Portal del Médico (Agenda)
    ├── paciente_home.html         # Portal del Paciente (Mis Citas)
    └── cubo.html                  # ⭐ Visualización del CUBO OLAP

🧬 6. Modelo Relacional OLTP
El sistema operativo gestiona las entidades transaccionales del negocio:

Entidades Principales
USUARIOS_WEB: Gestión centralizada de accesos (Admin, Médico, Paciente).

MEDICO: Almacena datos profesionales, especialidad, cédula y horario.

PACIENTE: Información demográfica e historial médico básico.

CITA: Tabla central que vincula Médico-Paciente-Tiempo con motivo y estado.
📊 7. Almacén de datos - Modelo Dimensional
Se diseñó un Esquema Estrella optimizado para consultas analíticas rápidas:

Tabla de Hechos: fact_citas
Almacena las métricas cuantitativas del negocio:

ingreso_estimado (Monto monetario).

duracion_consulta (Tiempo en minutos).

cantidad_citas (Contador).

Dimensiones
📅 dim_tiempo: Jerarquía Año → Trimestre → Mes → Día.

👨‍⚕️ dim_medico: Análisis por profesional y su rendimiento.

🩺 dim_especialidad: Análisis agrupado por área médica (Cardiología, etc.).

🧊 8. Cubo de datos OLAP
El módulo de BI permite responder preguntas estratégicas mediante navegación multidimensional:

Medidas (KPIs)
💰 Ingresos Totales: Suma monetaria de todas las consultas realizadas.

📉 Volumen de Citas: Total de interacciones médico-paciente.

👥 Total de Pacientes: Base de usuarios activos.

🩺 Especialidad Top: Área más rentable o demandada.

Operaciones en la Interfaz Web
Slice (Rebanar): Ver ingresos de un solo mes.

Dice (Dados): Comparar ingresos entre dos especialidades específicas.

Drill-Down (Desglosar): Ver detalle de citas por día dentro de un mes.

Roll-Up (Agrupar): Ver totales anuales.

🚀 10. Instalación y Ejecución
Requisitos previos
Python 3.10 o superior.

PostgreSQL (Local o cuenta en Supabase).

Consultar en: https://bdconsultoriofinal.onrender.com/
    
    DB -->|Extracción & Transformación| ETL
    ETL -->|Carga| DW
