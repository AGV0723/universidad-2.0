"""
CRUD para asignatura, pensum_asignatura y prerequisito.
El SUPERVISOR gestiona toda esta información.
"""
from db import ejecutar_query, ejecutar_comando, ejecutar_transaccion


# ASIGNATURA 

def listar_asignaturas():
    return ejecutar_query(
        "SELECT * FROM asignatura ORDER BY nombre"
    )

def obtener_asignatura(id_asignatura):
    return ejecutar_query(
        "SELECT * FROM asignatura WHERE id_asignatura = %s",
        (id_asignatura,), fetchone=True
    )

def crear_asignatura(codigo, nombre, creditos):
    """
    Crea una asignatura nueva (independiente del pensum).
    Las asignaturas son reutilizables entre programas.
    """
    if ejecutar_query(
        "SELECT id_asignatura FROM asignatura WHERE codigo = %s",
        (codigo,), fetchone=True
    ):
        return False, f"Ya existe una asignatura con código '{codigo}'."

    if creditos <= 0:
        return False, "Los créditos deben ser un número positivo."

    id_nuevo = ejecutar_comando(
        "INSERT INTO asignatura (codigo, nombre, creditos) VALUES (%s, %s, %s)",
        (codigo, nombre, creditos)
    )
    return True, id_nuevo


def actualizar_asignatura(id_asignatura, nombre=None, creditos=None):
    asig = obtener_asignatura(id_asignatura)
    if not asig:
        return False, "Asignatura no encontrada."

    campos, valores = [], []
    if nombre is not None:
        campos.append("nombre = %s"); valores.append(nombre)
    if creditos is not None:
        if creditos <= 0:
            return False, "Los créditos deben ser un número positivo."
        campos.append("creditos = %s"); valores.append(creditos)
    if not campos:
        return False, "No se proporcionaron datos."

    valores.append(id_asignatura)
    ejecutar_comando(
        f"UPDATE asignatura SET {', '.join(campos)} WHERE id_asignatura = %s",
        tuple(valores)
    )
    return True, "Asignatura actualizada."

def eliminar_asignatura(id_asignatura):
    """
    Solo elimina si la asignatura no está en ningún pensum
    ni en el historial académico.
    """
    if ejecutar_query(
        "SELECT id_pensum FROM pensum_asignatura WHERE id_asignatura = %s LIMIT 1",
        (id_asignatura,), fetchone=True
    ):
        return False, "No se puede eliminar: la asignatura está en uno o más pensum."

    if ejecutar_query(
        "SELECT id_historial FROM historial_academico WHERE id_asignatura = %s LIMIT 1",
        (id_asignatura,), fetchone=True
    ):
        return False, "No se puede eliminar: la asignatura tiene historial académico."

    ejecutar_comando(
        "DELETE FROM asignatura WHERE id_asignatura = %s",
        (id_asignatura,)
    )
    return True, "Asignatura eliminada."


# PLAN DE ESTUDIO (pensum_asignatura)

def listar_plan_estudio(id_pensum):
    """
    Devuelve todas las asignaturas de un pensum ordenadas por semestre.
    Incluye los prerequisitos de cada asignatura.
    """
    asignaturas = ejecutar_query(
        """SELECT pa.semestre, pa.obligatoria,
                  a.id_asignatura, a.codigo, a.nombre, a.creditos
           FROM pensum_asignatura pa
           JOIN asignatura a ON pa.id_asignatura = a.id_asignatura
           WHERE pa.id_pensum = %s
           ORDER BY pa.semestre, a.nombre""",
        (id_pensum,)
    )

    # Agregar prerequisitos a cada asignatura
    for asig in asignaturas:
        prereqs = ejecutar_query(
            """SELECT a.codigo, a.nombre
               FROM prerequisito p
               JOIN asignatura a ON p.id_prerequisito = a.id_asignatura
               WHERE p.id_pensum = %s AND p.id_asignatura = %s""",
            (id_pensum, asig["id_asignatura"])
        )
        asig["prerequisitos"] = prereqs

    return asignaturas


def agregar_asignatura_pensum(id_pensum, id_asignatura, semestre, obligatoria=True):
    """Agrega una asignatura a un pensum en un semestre específico."""
    from logic.programa import obtener_pensum
    pensum = obtener_pensum(id_pensum)
    if not pensum:
        return False, "Pensum no encontrado."

    if not obtener_asignatura(id_asignatura):
        return False, "Asignatura no encontrada."

    if semestre < 1 or semestre > pensum["total_semestres"]:
        return False, f"Semestre inválido. El pensum tiene {pensum['total_semestres']} semestres."

    if ejecutar_query(
        "SELECT id_pensum FROM pensum_asignatura WHERE id_pensum=%s AND id_asignatura=%s",
        (id_pensum, id_asignatura), fetchone=True
    ):
        return False, "La asignatura ya está en este pensum."

    ejecutar_comando(
        "INSERT INTO pensum_asignatura (id_pensum, id_asignatura, semestre, obligatoria) VALUES (%s,%s,%s,%s)",
        (id_pensum, id_asignatura, semestre, obligatoria)
    )
    return True, "Asignatura agregada al pensum."


def eliminar_asignatura_pensum(id_pensum, id_asignatura):
    """
    Elimina una asignatura del pensum.
    También elimina los prerequisitos asociados.
    """
    ejecutar_transaccion([
        ("DELETE FROM prerequisito WHERE id_pensum=%s AND (id_asignatura=%s OR id_prerequisito=%s)",
         (id_pensum, id_asignatura, id_asignatura)),
        ("DELETE FROM pensum_asignatura WHERE id_pensum=%s AND id_asignatura=%s",
         (id_pensum, id_asignatura))
    ])
    return True, "Asignatura eliminada del pensum."

# PREREQUISITOS 

def agregar_prerequisito(id_pensum, id_asignatura, id_prerequisito):
    """
    Registra que id_prerequisito debe aprobarse antes de tomar id_asignatura.
    Valida que ambas estén en el pensum y que no haya ciclos.
    """
    # Verificar que ambas estén en el pensum
    for id_asig in [id_asignatura, id_prerequisito]:
        if not ejecutar_query(
            "SELECT id_pensum FROM pensum_asignatura WHERE id_pensum=%s AND id_asignatura=%s",
            (id_pensum, id_asig), fetchone=True
        ):
            return False, f"La asignatura {id_asig} no está en este pensum."

    if id_asignatura == id_prerequisito:
        return False, "Una asignatura no puede ser prerequisito de sí misma."

    # Verificar que no se está creando un ciclo (B requiere A, y A ya requiere B)
    if ejecutar_query(
        "SELECT * FROM prerequisito WHERE id_pensum=%s AND id_asignatura=%s AND id_prerequisito=%s",
        (id_pensum, id_prerequisito, id_asignatura), fetchone=True
    ):
        return False, "Esto crearía un ciclo de prerequisitos."

    if ejecutar_query(
        "SELECT * FROM prerequisito WHERE id_pensum=%s AND id_asignatura=%s AND id_prerequisito=%s",
        (id_pensum, id_asignatura, id_prerequisito), fetchone=True
    ):
        return False, "Este prerequisito ya existe."

    ejecutar_comando(
        "INSERT INTO prerequisito (id_pensum, id_asignatura, id_prerequisito) VALUES (%s,%s,%s)",
        (id_pensum, id_asignatura, id_prerequisito)
    )
    return True, "Prerequisito agregado."

def eliminar_prerequisito(id_pensum, id_asignatura, id_prerequisito):
    ejecutar_comando(
        "DELETE FROM prerequisito WHERE id_pensum=%s AND id_asignatura=%s AND id_prerequisito=%s",
        (id_pensum, id_asignatura, id_prerequisito)
    )
    return True, "Prerequisito eliminado."

def listar_asignaturas_disponibles_para_semestre(id_pensum, semestre_a_cursar, id_estudiante):
    """
    Devuelve las asignaturas que el estudiante puede inscribir.
    Reglas:
    1. La asignatura debe estar en el pensum del estudiante
    2. semestre_asignatura <= semestre_a_cursar + 3
    3. Todos los prerequisitos deben estar APROBADOS en historial_academico
    4. La asignatura no debe estar ya aprobada
    """
    # Asignaturas en rango de semestre
    candidatas = ejecutar_query(
        """SELECT pa.semestre, a.id_asignatura, a.codigo, a.nombre, a.creditos
           FROM pensum_asignatura pa
           JOIN asignatura a ON pa.id_asignatura = a.id_asignatura
           WHERE pa.id_pensum = %s
             AND pa.semestre <= %s
           ORDER BY pa.semestre, a.nombre""",
        (id_pensum, semestre_a_cursar + 3)
    )

    disponibles = []
    for asig in candidatas:
        id_asig = asig["id_asignatura"]

        # Excluir ya aprobadas
        ya_aprobada = ejecutar_query(
            """SELECT id_historial FROM historial_academico
               WHERE id_estudiante=%s AND id_asignatura=%s AND estado='APROBADA'""",
            (id_estudiante, id_asig), fetchone=True
        )
        if ya_aprobada:
            continue

        # Verificar prerequisitos
        prereqs = ejecutar_query(
            "SELECT id_prerequisito FROM prerequisito WHERE id_pensum=%s AND id_asignatura=%s",
            (id_pensum, id_asig)
        )

        prereqs_ok = True
        for prereq in prereqs:
            aprobado = ejecutar_query(
                """SELECT id_historial FROM historial_academico
                   WHERE id_estudiante=%s AND id_asignatura=%s AND estado='APROBADA'""",
                (id_estudiante, prereq["id_prerequisito"]), fetchone=True
            )
            if not aprobado:
                prereqs_ok = False
                break

        if prereqs_ok:
            disponibles.append(asig)

    return disponibles


# ── Wrappers para rutas ────────────────────────────────────────
def listar_asignaturas_pensum(id_pensum):
    """Retorna asignaturas de un pensum (para ruta GET /pensum/<id>/plan)"""
    return listar_plan_estudio(id_pensum)

def quitar_asignatura_pensum(id_pensum, id_asignatura):
    """Elimina asignatura de pensum (para ruta DELETE)"""
    return eliminar_asignatura_pensum(id_pensum, id_asignatura)
