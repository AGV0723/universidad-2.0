"""
logic/codigo_detalle.py — CRUD para la tabla codigo_detalle.

Los códigos de detalle clasifican cada movimiento en cuenta_corriente.
  grupo COBRO → lo que se le cobra al estudiante (ej: PMAT, PCRE)
  grupo PAGO  → lo que paga el estudiante       (ej: MPAG, ANT, DESC, CRED)

Esta lógica está separada de regla_cobro.py para respetar el principio
de responsabilidad única: las reglas de cobro definen el MONTO,
los códigos de detalle clasifican el CONCEPTO del movimiento.
"""

from db import ejecutar_query, ejecutar_comando


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS
# ─────────────────────────────────────────────────────────────────────────────

def listar_codigos(grupo: str = None):
    """
    Devuelve todos los códigos de detalle.
    grupo: 'COBRO' | 'PAGO' | None (devuelve todos)
    """
    if grupo:
        return ejecutar_query(
            "SELECT * FROM codigo_detalle WHERE grupo = %s ORDER BY grupo, codigo",
            (grupo,)
        )
    return ejecutar_query(
        "SELECT * FROM codigo_detalle ORDER BY grupo, codigo"
    )


def obtener_codigo(id_codigo: int):
    """Obtiene un código por su PK numérica."""
    return ejecutar_query(
        "SELECT * FROM codigo_detalle WHERE id_codigo = %s",
        (id_codigo,), fetchone=True
    )


def obtener_codigo_por_codigo(codigo: str):
    """
    Obtiene un código por su código alfanumérico (ej: 'PMAT', 'MPAG').
    Es la función que usa la lógica de inscripción para calcular cobros.
    """
    return ejecutar_query(
        "SELECT * FROM codigo_detalle WHERE codigo = %s",
        (codigo,), fetchone=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# CREACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def crear_codigo(codigo: str, descripcion: str, grupo: str):
    """
    Crea un nuevo código de detalle.
    Valida unicidad del código alfanumérico y que el grupo sea válido.
    Devuelve (True, id_nuevo) o (False, mensaje_error).
    """
    grupos_validos = ("COBRO", "PAGO")
    if grupo not in grupos_validos:
        return False, f"Grupo inválido. Debe ser: {', '.join(grupos_validos)}"

    codigo = codigo.strip().upper()
    if not codigo:
        return False, "El código no puede estar vacío."

    if ejecutar_query(
        "SELECT id_codigo FROM codigo_detalle WHERE codigo = %s",
        (codigo,), fetchone=True
    ):
        return False, f"Ya existe un código de detalle con código '{codigo}'."

    id_nuevo = ejecutar_comando(
        "INSERT INTO codigo_detalle (codigo, descripcion, grupo) VALUES (%s, %s, %s)",
        (codigo, descripcion, grupo)
    )
    return True, id_nuevo


# ─────────────────────────────────────────────────────────────────────────────
# ACTUALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def actualizar_codigo(id_codigo: int, descripcion: str = None, grupo: str = None):
    """
    Actualiza la descripción y/o grupo de un código existente.
    No se permite cambiar el código alfanumérico (es una clave de negocio).
    Devuelve (True, mensaje) o (False, mensaje_error).
    """
    if not obtener_codigo(id_codigo):
        return False, "Código de detalle no encontrado."

    campos, valores = [], []

    if descripcion is not None:
        campos.append("descripcion = %s")
        valores.append(descripcion)

    if grupo is not None:
        grupos_validos = ("COBRO", "PAGO")
        if grupo not in grupos_validos:
            return False, f"Grupo inválido. Debe ser: {', '.join(grupos_validos)}"
        campos.append("grupo = %s")
        valores.append(grupo)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_codigo)
    ejecutar_comando(
        f"UPDATE codigo_detalle SET {', '.join(campos)} WHERE id_codigo = %s",
        tuple(valores)
    )
    return True, "Código de detalle actualizado correctamente."


# ─────────────────────────────────────────────────────────────────────────────
# ELIMINACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def eliminar_codigo(id_codigo: int):
    """
    Elimina un código de detalle.
    Regla de negocio: no se puede eliminar si tiene movimientos en cuenta_corriente,
    porque eso rompería el historial financiero del estudiante.
    Devuelve (True, mensaje) o (False, mensaje_error).
    """
    if not obtener_codigo(id_codigo):
        return False, "Código de detalle no encontrado."

    en_uso = ejecutar_query(
        "SELECT id_movimiento FROM cuenta_corriente WHERE id_codigo_detalle = %s LIMIT 1",
        (id_codigo,), fetchone=True
    )
    if en_uso:
        return False, (
            "No se puede eliminar: el código tiene movimientos registrados en "
            "cuenta corriente. Considere desactivarlo en su lugar."
        )

    ejecutar_comando(
        "DELETE FROM codigo_detalle WHERE id_codigo = %s",
        (id_codigo,)
    )
    return True, "Código de detalle eliminado correctamente."