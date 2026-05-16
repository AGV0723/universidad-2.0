"""
db.py — Conexión a MySQL usando mysql-connector-python.

Usa un pool de conexiones para no abrir/cerrar una conexión por cada petición (para optimizar).
Al arrancar la aplicación, se crean 5 conexiones y se dejan abiertas y listas 
(pool_size=5). Cuando llega una petición, toma una conexión disponible, la usa, 
y la devuelve al pool (no la cierra).
"""
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv #librería de python que lee el archivo .emnv y pone las "variables de entorno" disponibles para od.getenv()
import os

load_dotenv() # carga el .env y mete las variables en el entorno del sistema

# Configuración del pool de conexiones
# pool_size=5 significa que hay hasta 5 conexiones simultáneas disponibles
_pool = pooling.MySQLConnectionPool(
    pool_name="uninorte_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "uninorte"),
)


def get_connection():
    """
    Obtiene una conexión del pool.
    Úsala con 'with get_connection() as conn:' para que se devuelva automáticamente.
    """
    return _pool.get_connection()


def ejecutar_query(sql: str, params: tuple = (), fetchone: bool = False):
    """
    Ejecuta un SELECT y devuelve los resultados como lista de diccionarios.
    Si fetchone=True, devuelve solo el primer resultado o None.
    """
    conn = get_connection()
    try:
        # dictionary=True hace que cada fila sea un dict {columna: valor}
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetchone:
            return cursor.fetchone()
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def ejecutar_comando(sql: str, params: tuple = ()):
    """
    Ejecuta INSERT, UPDATE o DELETE.
    Devuelve el id del último registro insertado (útil para INSERT).
    Hace commit automático.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def ejecutar_transaccion(operaciones: list):
    """
    Ejecuta múltiples operaciones SQL en una sola transacción.
    operaciones = [(sql, params), (sql, params), ...]
    Si alguna falla, hace rollback de todas.
    Devuelve lista de lastrowid de cada operación.
    """
    conn = get_connection()
    ids = []
    try:
        cursor = conn.cursor()
        for sql, params in operaciones:
            cursor.execute(sql, params)
            ids.append(cursor.lastrowid)
        conn.commit()
        return ids
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
