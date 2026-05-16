"""
CRUD para regla_cobro.
El SUPERVISOR define las reglas por periodo, programa y modalidad.
"""
from db import ejecutar_query, ejecutar_comando

# REGLA DE COBRO 

def listar_reglas(id_periodo=None, id_programa=None):
    condiciones = []
    params = []

    if id_periodo:
        condiciones.append("rc.id_periodo = %s"); params.append(id_periodo)
    if id_programa:
        condiciones.append("rc.id_programa = %s"); params.append(id_programa)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    return ejecutar_query(
        f"""SELECT rc.*,
                   p.codigo AS codigo_periodo, p.descripcion AS desc_periodo,
                   pr.nombre AS nombre_programa
            FROM regla_cobro rc
            JOIN periodo_academico p ON rc.id_periodo = p.id_periodo
            JOIN programa_academico pr ON rc.id_programa = pr.id_programa
            {where}
            ORDER BY p.fecha_inicio DESC, pr.nombre, rc.modalidad""",
        tuple(params)
    )

def obtener_regla(id_regla):
    """Obtiene una regla por su ID."""
    return ejecutar_query(
        "SELECT * FROM regla_cobro WHERE id_regla = %s",
        (id_regla,), fetchone=True
    )

def obtener_regla_por_parametros(id_periodo, id_programa, modalidad):
    """
    Obtiene la regla de cobro específica para periodo + programa + modalidad.
    Esta es la función clave para calcular el monto de la inscripción.
    """
    return ejecutar_query(
        """SELECT * FROM regla_cobro
           WHERE id_periodo=%s AND id_programa=%s AND modalidad=%s""",
        (id_periodo, id_programa, modalidad), fetchone=True
    )

def crear_regla(modalidad, valor, id_periodo, id_programa):
    """
    Crea una regla de cobro.
    modalidad: GLOBAL | POR_CREDITOS
    valor: monto total (GLOBAL) o monto por crédito (POR_CREDITOS)
    """
    modalidades_validas = ("GLOBAL", "POR_CREDITOS")
    if modalidad not in modalidades_validas:
        return False, f"Modalidad inválida. Debe ser: {', '.join(modalidades_validas)}"

    if valor <= 0:
        return False, "El valor debe ser mayor que cero."

    if ejecutar_query(
        "SELECT id_regla FROM regla_cobro WHERE id_periodo=%s AND id_programa=%s AND modalidad=%s",
        (id_periodo, id_programa, modalidad), fetchone=True
    ):
        return False, "Ya existe una regla para ese periodo, programa y modalidad."

    id_nuevo = ejecutar_comando(
        "INSERT INTO regla_cobro (modalidad, valor, id_periodo, id_programa) VALUES (%s,%s,%s,%s)",
        (modalidad, valor, id_periodo, id_programa)
    )
    return True, id_nuevo

def actualizar_regla(id_regla, valor):
    """Solo se puede actualizar el valor de la regla."""
    if valor <= 0:
        return False, "El valor debe ser mayor que cero."
    ejecutar_comando(
        "UPDATE regla_cobro SET valor = %s WHERE id_regla = %s",
        (valor, id_regla)
    )
    return True, "Regla actualizada."

def eliminar_regla(id_regla):
    """
    Solo elimina si no hay inscripciones que usen esta modalidad en ese periodo/programa.
    """
    regla = ejecutar_query(
        "SELECT * FROM regla_cobro WHERE id_regla = %s", (id_regla,), fetchone=True
    )
    if not regla:
        return False, "Regla no encontrada."

    if ejecutar_query(
        """SELECT id_inscripcion FROM inscripcion
           WHERE id_periodo=%s AND id_programa=%s AND modalidad_cobro=%s LIMIT 1""",
        (regla["id_periodo"], regla["id_programa"], regla["modalidad"]), fetchone=True
    ):
        return False, "No se puede eliminar: ya hay inscripciones con esta regla."

    ejecutar_comando("DELETE FROM regla_cobro WHERE id_regla = %s", (id_regla,))
    return True, "Regla eliminada."