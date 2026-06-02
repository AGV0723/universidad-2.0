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
                     correo=None, telefono=None,
                     username=None, password=None):
    """
    Registra un nuevo estudiante y crea automáticamente:
    1. PERSONA (si no existe)
    2. USUARIO con rol ESTUDIANTE
    
    Parámetros adicionales:
    - username: para crear usuario (requerido)
    - password: contraseña del usuario (requerido)
    """
    from db import ejecutar_transaccion
    
    # Validar unicidad del estudiante
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

    # Si se proporciona username/password, validar y crear usuario
    id_persona = None
    if username or password:
        if not username or not password:
            return False, "Si crea un usuario, debe proporcionar username Y password."
        
        # Validar unicidad del username
        if ejecutar_query(
            "SELECT id_usuario FROM usuario WHERE username = %s",
            (username,), fetchone=True
        ):
            return False, f"El username '{username}' ya está en uso."
        
        # Obtener ID del rol ESTUDIANTE
        rol = ejecutar_query(
            "SELECT id_rol FROM rol WHERE nombre = %s",
            ('ESTUDIANTE',), fetchone=True
        )
        if not rol:
            return False, "El rol ESTUDIANTE no existe en la base de datos."
        
        id_rol_estudiante = rol['id_rol']
        
        # Crear PERSONA
        try:
            id_persona = ejecutar_comando(
                """INSERT INTO persona (primer_nombre, segundo_nombre, apellido, 
                   segundo_apellido, documento_identidad, correo, telefono)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (primer_nombre, segundo_nombre, apellido, segundo_apellido,
                 documento_identidad, correo, telefono)
            )
        except Exception as e:
            # Si la persona ya existe por documento, obtenerla
            persona = ejecutar_query(
                "SELECT id_persona FROM persona WHERE documento_identidad = %s",
                (documento_identidad,), fetchone=True
            )
            if persona:
                id_persona = persona['id_persona']
            else:
                return False, f"Error al crear persona: {str(e)}"
        
        # Hashear contraseña
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        
        # Crear USUARIO
        try:
            ejecutar_comando(
                """INSERT INTO usuario (username, password_hash, correo, id_persona, id_rol, activo)
                   VALUES (%s, %s, %s, %s, %s, TRUE)""",
                (username, password_hash, correo, id_persona, id_rol_estudiante)
            )
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"

    # Crear ESTUDIANTE
    try:
        id_nuevo = ejecutar_comando(
            """INSERT INTO estudiante
               (codigo_estudiantil, documento_identidad, primer_nombre, segundo_nombre,
                apellido, segundo_apellido, correo, telefono, id_programa, id_pensum)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (codigo_estudiantil, documento_identidad, primer_nombre, segundo_nombre,
             apellido, segundo_apellido, correo, telefono, id_programa, id_pensum)
        )
        
        mensaje = "Estudiante creado"
        if username:
            mensaje += f" con usuario '{username}' (rol ESTUDIANTE) activado."
        
        return True, id_nuevo, mensaje
    except Exception as e:
        return False, f"Error al crear estudiante: {str(e)}"

def actualizar_estudiante(id_estudiante, **kwargs):
    """
    Actualiza campos del estudiante.
    Campos permitidos: primer_nombre, segundo_nombre, apellido, segundo_apellido,
                       correo, telefono, documento_identidad, activo, id_programa, id_pensum
    
    Si se actualizan datos personales (nombres, documento, correo, teléfono), 
    también se sincronizan en PERSONA y USUARIO.
    """
    estudiante = obtener_estudiante(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado."

    campos_permitidos = {
        "primer_nombre", "segundo_nombre", "apellido", "segundo_apellido",
        "correo", "telefono", "documento_identidad", "activo", "id_programa", "id_pensum"
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
    
    # Sincronizar con PERSONA y USUARIO si se cambian datos personales
    campos_personales = {"primer_nombre", "segundo_nombre", "apellido", "segundo_apellido", "correo", "telefono", "documento_identidad"}
    if any(k in kwargs for k in campos_personales):
        try:
            # Usar documento nuevo si cambió, sino el viejo
            doc_identidad = kwargs.get("documento_identidad", estudiante["documento_identidad"])
            
            # Actualizar PERSONA usando documento_identidad como clave
            persona_data = {k: v for k, v in kwargs.items() if k in campos_personales}
            if persona_data:
                persona_campos = []
                persona_valores = []
                for campo, valor in persona_data.items():
                    persona_campos.append(f"{campo} = %s")
                    persona_valores.append(valor)
                persona_valores.append(estudiante["documento_identidad"])  # Usar DOC VIEJO para el WHERE
                ejecutar_comando(
                    f"UPDATE persona SET {', '.join(persona_campos)} WHERE documento_identidad = %s",
                    tuple(persona_valores)
                )
            
            # Actualizar correo en USUARIO si cambió
            if "correo" in kwargs:
                usuario = ejecutar_query(
                    """SELECT u.id_usuario FROM usuario u
                       JOIN persona p ON u.id_persona = p.id_persona
                       WHERE p.documento_identidad = %s""",
                    (estudiante["documento_identidad"],), fetchone=True  # Usar DOC VIEJO
                )
                if usuario:
                    ejecutar_comando(
                        "UPDATE usuario SET correo = %s WHERE id_usuario = %s",
                        (kwargs["correo"], usuario["id_usuario"])
                    )
        except Exception as e:
            # Si falla la sincronización, la actualización principal ya se hizo
            import traceback
            traceback.print_exc()
    
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


def eliminar_estudiante(id_estudiante):
    """
    Elimina un estudiante y todas sus relaciones en cascada.
    
    Orden de eliminación:
    1. Verifica si existe historial_academico (no se puede eliminar si existe)
    2. Elimina movimientos en cuenta_corriente (FK con RESTRICT)
    3. Elimina las inscripciones (FK con CASCADE automático)
    4. Elimina el usuario si existe (para poder eliminar la persona)
    5. Elimina la persona asociada si existe
    6. Elimina finalmente el estudiante
    """
    estudiante = obtener_estudiante(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado."
    
    # Verificar si hay historial academico
    historial = ejecutar_query(
        "SELECT COUNT(*) as count FROM historial_academico WHERE id_estudiante = %s",
        (id_estudiante,), fetchone=True
    )
    if historial and historial["count"] > 0:
        return False, f"No se puede eliminar: el estudiante tiene {historial['count']} registro(s) en historial académico."
    
    try:
        # 1. Eliminar movimientos de cuenta_corriente (RESTRICT FK)
        ejecutar_comando(
            "DELETE FROM cuenta_corriente WHERE id_estudiante = %s",
            (id_estudiante,)
        )
        
        # 2. Eliminar inscripciones (CASCADE automático eliminará inscripcion_asignatura)
        ejecutar_comando(
            "DELETE FROM inscripcion WHERE id_estudiante = %s",
            (id_estudiante,)
        )
        
        # 3. Buscar y eliminar usuario y persona si existen
        usuario = ejecutar_query(
            """SELECT u.id_usuario, u.id_persona FROM usuario u
               JOIN persona p ON u.id_persona = p.id_persona
               WHERE p.documento_identidad = %s""",
            (estudiante["documento_identidad"],), fetchone=True
        )
        
        if usuario:
            ejecutar_comando(
                "DELETE FROM usuario WHERE id_usuario = %s",
                (usuario["id_usuario"],)
            )
            ejecutar_comando(
                "DELETE FROM persona WHERE id_persona = %s",
                (usuario["id_persona"],)
            )
        
        # 4. Finalmente eliminar el estudiante
        ejecutar_comando(
            "DELETE FROM estudiante WHERE id_estudiante = %s",
            (id_estudiante,)
        )
        
        return True, "Estudiante eliminado completamente."
    except Exception as e:
        return False, f"Error al eliminar estudiante: {str(e)}"

