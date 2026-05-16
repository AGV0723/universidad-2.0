"""logic/pensum.py - Lógica de Pensum"""
from db import ejecutar_query, ejecutar_comando

def listar_pensum_programa(id_programa):
    """Retorna pensumes de un programa."""
    return ejecutar_query(
        "SELECT * FROM pensum WHERE id_programa = %s ORDER BY version DESC",
        (id_programa,)
    )

def obtener_pensum(id_pensum):
    """Retorna un pensum por ID."""
    return ejecutar_query(
        "SELECT * FROM pensum WHERE id_pensum = %s",
        (id_pensum,), fetchone=True
    )

def crear_pensum(id_programa, version, total_semestres, fecha_vigencia):
    """Crea un pensum."""
    # Validar que el programa existe
    if not ejecutar_query(
        "SELECT id_programa FROM programa_academico WHERE id_programa = %s",
        (id_programa,), fetchone=True
    ):
        return False, "Programa no encontrado"
    
    # Validar unicidad de versión por programa
    if ejecutar_query(
        "SELECT id_pensum FROM pensum WHERE id_programa = %s AND version = %s",
        (id_programa, version), fetchone=True
    ):
        return False, f"Ya existe un pensum con la versión '{version}' en este programa"
    
    id_nuevo = ejecutar_comando(
        """INSERT INTO pensum (id_programa, version, total_semestres, fecha_vigencia)
           VALUES (%s, %s, %s, %s)""",
        (id_programa, version, total_semestres, fecha_vigencia)
    )
    return True, id_nuevo

def actualizar_pensum(id_pensum, **kwargs):
    """Actualiza un pensum."""
    pensum = obtener_pensum(id_pensum)
    if not pensum:
        return False, "Pensum no encontrado"
    
    campos_permitidos = {"version", "total_semestres", "fecha_vigencia"}
    campos, valores = [], []
    
    for campo, valor in kwargs.items():
        if campo in campos_permitidos and valor is not None:
            campos.append(f"{campo} = %s")
            valores.append(valor)
    
    if not campos:
        return False, "No se proporcionaron datos para actualizar"
    
    valores.append(id_pensum)
    ejecutar_comando(
        f"UPDATE pensum SET {', '.join(campos)} WHERE id_pensum = %s",
        tuple(valores)
    )
    return True, "Pensum actualizado"

def eliminar_pensum(id_pensum):
    """Elimina un pensum."""
    pensum = obtener_pensum(id_pensum)
    if not pensum:
        return False, "Pensum no encontrado"
    
    # Verificar que no haya asignaciones activas
    if ejecutar_query(
        "SELECT id_pensum_asignatura FROM pensum_asignatura WHERE id_pensum = %s LIMIT 1",
        (id_pensum,), fetchone=True
    ):
        return False, "No se puede eliminar: el pensum tiene asignaciones"
    
    ejecutar_comando(
        "DELETE FROM pensum WHERE id_pensum = %s",
        (id_pensum,)
    )
    return True, "Pensum eliminado"
