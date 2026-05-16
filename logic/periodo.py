"""
CRUD para periodo_academico
"""
from db import ejecutar_query, ejecutar_comando

def listar_periodos(solo_activos=False):
    sql = "SELECT * FROM periodo_academico"
    if solo_activos:
        sql += " WHERE activo = TRUE"
    sql += " ORDER BY fecha_inicio DESC"
    return ejecutar_query(sql)

def obtener_periodo(id_periodo):
    return ejecutar_query(
        "SELECT * FROM periodo_academico WHERE id_periodo = %s",
        (id_periodo,), fetchone=True
    )

def crear_periodo(codigo, descripcion, fecha_inicio, fecha_fin):
    if ejecutar_query(
        "SELECT id_periodo FROM periodo_academico WHERE codigo = %s",
        (codigo,), fetchone=True
    ):
        return False, f"Ya existe un periodo con código '{codigo}'."

    id_nuevo = ejecutar_comando(
        "INSERT INTO periodo_academico (codigo, descripcion, fecha_inicio, fecha_fin) VALUES (%s,%s,%s,%s)",
        (codigo, descripcion, fecha_inicio, fecha_fin)
    )
    return True, id_nuevo

def actualizar_periodo(id_periodo, descripcion=None, fecha_inicio=None, fecha_fin=None, activo=None):
    if not obtener_periodo(id_periodo):
        return False, "Periodo no encontrado."

    campos, valores = [], []
    if descripcion  is not None: campos.append("descripcion = %s");  valores.append(descripcion)
    if fecha_inicio is not None: campos.append("fecha_inicio = %s"); valores.append(fecha_inicio)
    if fecha_fin    is not None: campos.append("fecha_fin = %s");    valores.append(fecha_fin)
    if activo       is not None: campos.append("activo = %s");       valores.append(activo)

    if not campos:
        return False, "No se proporcionaron datos."

    valores.append(id_periodo)
    ejecutar_comando(
        f"UPDATE periodo_academico SET {', '.join(campos)} WHERE id_periodo = %s",
        tuple(valores)
    )
    return True, "Periodo actualizado."
