"""
CRUD para la tabla estudiante.
El SUPERVISOR registra estudiantes; el ASISTENTE gestiona cobros.
"""
from db import ejecutar_query, ejecutar_comando


def listar_estudiantes(solo_activos=True, id_programa=None):
    """Devuelve estudiantes con nombre del programa."""
    condiciones = ["e.activo = TRUE"] if solo_activos else []
    params = []

    if id_programa:
        condiciones.append("e.id_programa = %s")
        params.append(id_programa)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    return ejecutar_query(
        f"""SELECT e.*,
                   CONCAT(e.primer_nombre, ' ', COALESCE(e.segundo_nombre, ''), ' ',
                          e.apellido, ' ', COALESCE(e.segundo_apellido, '')) AS nombre_completo,
                   pr.nombre AS nombre_programa,
                   pe.version AS version_pensum
            FROM estudiante e
            JOIN programa_academico pr ON e.id_programa = pr.id_programa
            JOIN pensum pe ON e.id_pensum = pe.id_pensum
            {where}
            ORDER BY e.apellido, e.primer_nombre""",
        tuple(params)
    )


def obtener_estudiante(id_estudiante):
    return ejecutar_query(
        """SELECT e.*,
                  CONCAT(e.primer_nombre, ' ', COALESCE(e.segundo_nombre,''), ' ',
                         e.apellido, ' ', COALESCE(e.segundo_apellido,'')) AS nombre_completo,
                  pr.nombre AS nombre_programa,
                  pe.version AS version_pensum, pe.total_semestres
           FROM estudiante e
           JOIN programa_academico pr ON e.id_programa = pr.id_programa
           JOIN pensum pe ON e.id_pensum = pe.id_pensum
           WHERE e.id_estudiante = %s""",
        (id_estudiante,), fetchone=True
    )


def buscar_por_codigo(codigo_estudiantil):
    return ejecutar_query(
        "SELECT * FROM estudiante WHERE codigo_estudiantil = %s",
        (codigo_estudiantil,), fetchone=True
    )


def crear_estudiante(codigo_estudiantil, documento_identidad, primer_nombre,
                     apellido, id_programa, id_pensum,
                     segundo_nombre=None, segundo_apellido=None,
                     correo=None, telefono=None):
    """
    Registra un nuevo estudiante.
    Valida que el pensum pertenezca al programa indicado.
    """
    # Validar unicidad
    if ejecutar_query(
        "SELECT id_estudiante FROM estudiante WHERE codigo_estudiantil = %s",
        (codigo_estudiantil,), fetchone=True
    ):
        return False, f"Ya existe un estudiante con código '{codigo_estudiantil}'."

    if ejecutar_query(
        "SELECT id_estudiante FROM estudiante WHERE documento_identidad = %s",
        (documento_identidad,), fetchone=True
    ):
        return False, "Ya existe un estudiante con ese documento de identidad."

    # Validar que el pensum pertenece al programa
    if not ejecutar_query(
        "SELECT id_pensum FROM pensum WHERE id_pensum=%s AND id_programa=%s AND activo=TRUE",
        (id_pensum, id_programa), fetchone=True
    ):
        return False, "El pensum no pertenece al programa indicado o no está activo."

    id_nuevo = ejecutar_comando(
        """INSERT INTO estudiante
           (codigo_estudiantil, documento_identidad, primer_nombre, segundo_nombre,
            apellido, segundo_apellido, correo, telefono, id_programa, id_pensum)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (codigo_estudiantil, documento_identidad, primer_nombre, segundo_nombre,
         apellido, segundo_apellido, correo, telefono, id_programa, id_pensum)
    )
    return True, id_nuevo

def actualizar_estudiante(id_estudiante, **kwargs):
    """
    Actualiza campos del estudiante.
    Campos permitidos: primer_nombre, segundo_nombre, apellido, segundo_apellido,
                       correo, telefono, activo, id_programa, id_pensum
    """
    estudiante = obtener_estudiante(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado."

    campos_permitidos = {
        "primer_nombre", "segundo_nombre", "apellido", "segundo_apellido",
        "correo", "telefono", "activo", "id_programa", "id_pensum"
    }

    campos, valores = [], []
    for campo, valor in kwargs.items():
        if campo in campos_permitidos and valor is not None:
            campos.append(f"{campo} = %s")
            valores.append(valor)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    # Si se cambia programa o pensum, validar coherencia
    nuevo_programa = kwargs.get("id_programa", estudiante["id_programa"])
    nuevo_pensum   = kwargs.get("id_pensum",   estudiante["id_pensum"])

    if not ejecutar_query(
        "SELECT id_pensum FROM pensum WHERE id_pensum=%s AND id_programa=%s",
        (nuevo_pensum, nuevo_programa), fetchone=True
    ):
        return False, "El pensum no pertenece al programa indicado."

    valores.append(id_estudiante)
    ejecutar_comando(
        f"UPDATE estudiante SET {', '.join(campos)} WHERE id_estudiante = %s",
        tuple(valores)
    )
    return True, "Estudiante actualizado."


def desactivar_estudiante(id_estudiante):
    """Borrado lógico: desactiva el estudiante (para estudiantes inactivos y no eliminar el registro de la base de datos para siempre)."""
    if not obtener_estudiante(id_estudiante):
        return False, "Estudiante no encontrado."
    ejecutar_comando(
        "UPDATE estudiante SET activo = FALSE WHERE id_estudiante = %s",
        (id_estudiante,)
    )
    return True, "Estudiante desactivado."
