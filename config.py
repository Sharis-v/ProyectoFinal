import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'una_clave_secreta_por_defecto')
    # Usamos la misma BD para OLTP y OLAP en este ejemplo, 
    # pero lógicamente están separadas por esquemas.
    DATABASE_URL = os.getenv('DATABASE_URL')