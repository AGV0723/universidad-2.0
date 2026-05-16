"""
CRUD para programa_academico y pensum.
El SUPERVISOR es quien gestiona esta información.
"""
from db import ejecutar_query, ejecutar_comando

#  PROGRAMA ACADÉMICO 

def listar_programas(solo_activos=True):
    """Devuelve todos los programas académicos."""
    sql = "SELECT * FROM programa_academico"
    if solo_activos:
        sql += " WHERE activo = TRUE"
    sql += " ORDER BY nombre"
    return ejecutar_query(sql)

def obtener_programa(id_programa):
    """Devuelve un programa por su ID."""
    return ejecutar_query(
        "SELECT * FROM programa_academico WHERE id_programa = %s",
        (id_programa,), fetchone=True
    )

def crear_programa(codigo, nombre, nivel):
    """
    Inserta un nuevo programa académico.
    nivel debe ser: PREGRADO o POSGRADO
    """
    if ejecutar_query(
        "SELECT id_programa FROM programa_academico WHERE codigo = %s",
        (codigo,), fetchone=True
    ):
        return False, "Ya existe un programa con ese código."

    niveles_validos = ("PREGRADO", "POSGRADO")
    if nivel not in niveles_validos:
        return False, f"Nivel inválido. Debe ser: {', '.join(niveles_validos)}"

    id_nuevo = ejecutar_comando(
        "INSERT INTO programa_academico (codigo, nombre, nivel) VALUES (%s, %s, %s)",
        (codigo, nombre, nivel)
    )
    return True, id_nuevo


def actualizar_programa(id_programa, nombre=None, nivel=None, activo=None):
    """Actualiza campos de un programa académico ya existente."""
    programa = obtener_programa(id_programa)
    if not programa:
        return False, "Programa no encontrado."

    campos = []
    valores = []

    if nombre is not None:
        campos.append("nombre = %s")
        valores.append(nombre)
    if nivel is not None:
        niveles_validos = ("PREGRADO", "POSGRADO")
        if nivel not in niveles_validos:
            return False, f"Nivel inválido. Debe ser: {', '.join(niveles_validos)}"
        campos.append("nivel = %s")
        valores.append(nivel)
    if activo is not None:
        campos.append("activo = %s")
        valores.append(activo)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_programa)
    ejecutar_comando(
        f"UPDATE programa_academico SET {', '.join(campos)} WHERE id_programa = %s",
        tuple(valores)
    )
    return True, "Programa actualizado."


def eliminar_programa(id_programa):
    """
    Desactiva un programa (borrado lógico).
    No eliminamos físicamente para preservar un historial.
    """
    if not obtener_programa(id_programa):
        return False, "Programa no encontrado."
    ejecutar_comando(
        "UPDATE programa_academico SET activo = FALSE WHERE id_programa = %s",
        (id_programa,)
    )
    return True, "Programa desactivado."

# PENSUM 

def listar_pensum(id_programa=None):
    """Devuelve los pensum, opcionalmente filtrados por programa."""
    if id_programa:
        return ejecutar_query(
            """SELECT p.*, pr.nombre AS nombre_programa
               FROM pensum p
               JOIN programa_academico pr ON p.id_programa = pr.id_programa
               WHERE p.id_programa = %s AND p.activo = TRUE
               ORDER BY p.fecha_vigencia DESC""",
            (id_programa,)
        )
    return ejecutar_query(
        """SELECT p.*, pr.nombre AS nombre_programa
           FROM pensum p
           JOIN programa_academico pr ON p.id_programa = pr.id_programa
           WHERE p.activo = TRUE
           ORDER BY pr.nombre, p.fecha_vigencia DESC"""
    )

def obtener_pensum(id_pensum):
    return ejecutar_query(
        """SELECT p.*, pr.nombre AS nombre_programa
           FROM pensum p
           JOIN programa_academico pr ON p.id_programa = pr.id_programa
           WHERE p.id_pensum = %s""",
        (id_pensum,), fetchone=True
    )

def crear_pensum(id_programa, version, total_semestres, fecha_vigencia):
    """
    Crea un nuevo pensum para un programa.
    La combinación (id_programa, version) debe ser única.
    """
    if not obtener_programa(id_programa):
        return False, "El programa no existe."

    if ejecutar_query(
        "SELECT id_pensum FROM pensum WHERE id_programa = %s AND version = %s",
        (id_programa, version), fetchone=True
    ):
        return False, f"Ya existe un pensum versión '{version}' para ese programa."

    id_nuevo = ejecutar_comando(
        "INSERT INTO pensum (id_programa, version, total_semestres, fecha_vigencia) VALUES (%s,%s,%s,%s)",
        (id_programa, version, total_semestres, fecha_vigencia)
    )
    return True, id_nuevo

def actualizar_pensum(id_pensum, total_semestres=None, fecha_vigencia=None, activo=None):
    """Actualiza un pensum existente."""
    if not obtener_pensum(id_pensum):
        return False, "Pensum no encontrado."

    campos, valores = [], []
    if total_semestres is not None:
        campos.append("total_semestres = %s"); valores.append(total_semestres)
    if fecha_vigencia is not None:
        campos.append("fecha_vigencia = %s"); valores.append(fecha_vigencia)
    if activo is not None:
        campos.append("activo = %s"); valores.append(activo)
    if not campos:
        return False, "No se proporcionaron datos."

    valores.append(id_pensum)
    ejecutar_comando(
        f"UPDATE pensum SET {', '.join(campos)} WHERE id_pensum = %s",
        tuple(valores)
    )
    return True, "Pensum actualizado."
