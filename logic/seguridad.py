"""
logic/seguridad.py — Lógica de negocio para el módulo de Seguridad y Acceso.

Cubre:
  - Roles (CRUD)
  - Personas (CRUD)
  - Usuarios (CRUD + login + cambio de contraseña)
  - Menús (CRUD + árbol jerárquico)
  - Asignación de menús a roles (rol_menu)
  - Decorador `requiere_rol` para proteger rutas por rol

Decisiones de diseño:
  - Las contraseñas se almacenan con SHA-256 (sin librerías externas).
    Para producción real se recomienda bcrypt o argon2.
  - La "sesión" se maneja con flask.session (cookie firmada con SECRET_KEY).
  - El ADMINISTRADOR tiene acceso a TODO sin necesidad de entradas en rol_menu.
"""

import hashlib
import functools
from flask import session
from db import ejecutar_query, ejecutar_comando


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de contraseña
# ─────────────────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    """Devuelve el SHA-256 hex de la contraseña en texto plano."""
    return hashlib.sha256(plain.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────────────────────────────────────

def listar_roles():
    return ejecutar_query("SELECT * FROM rol ORDER BY nombre")


def obtener_rol(id_rol: int):
    return ejecutar_query(
        "SELECT * FROM rol WHERE id_rol = %s",
        (id_rol,), fetchone=True
    )


def crear_rol(nombre: str, descripcion: str = None):
    """Crea un rol. El nombre debe ser único."""
    nombre = nombre.upper().strip()
    if ejecutar_query(
        "SELECT id_rol FROM rol WHERE nombre = %s", (nombre,), fetchone=True
    ):
        return False, f"Ya existe un rol con nombre '{nombre}'."

    id_nuevo = ejecutar_comando(
        "INSERT INTO rol (nombre, descripcion) VALUES (%s, %s)",
        (nombre, descripcion)
    )
    return True, id_nuevo


def actualizar_rol(id_rol: int, nombre: str = None, descripcion: str = None):
    rol = obtener_rol(id_rol)
    if not rol:
        return False, "Rol no encontrado."

    campos, valores = [], []
    if nombre:
        nombre = nombre.upper().strip()
        existe = ejecutar_query(
            "SELECT id_rol FROM rol WHERE nombre = %s AND id_rol != %s",
            (nombre, id_rol), fetchone=True
        )
        if existe:
            return False, f"Ya existe otro rol con nombre '{nombre}'."
        campos.append("nombre = %s"); valores.append(nombre)
    if descripcion is not None:
        campos.append("descripcion = %s"); valores.append(descripcion)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_rol)
    ejecutar_comando(
        f"UPDATE rol SET {', '.join(campos)} WHERE id_rol = %s",
        tuple(valores)
    )
    return True, "Rol actualizado."


def eliminar_rol(id_rol: int):
    """Elimina un rol sólo si no tiene usuarios asignados."""
    if ejecutar_query(
        "SELECT id_usuario FROM usuario WHERE id_rol = %s LIMIT 1",
        (id_rol,), fetchone=True
    ):
        return False, "No se puede eliminar el rol: tiene usuarios asignados."
    ejecutar_comando("DELETE FROM rol WHERE id_rol = %s", (id_rol,))
    return True, "Rol eliminado."


# ─────────────────────────────────────────────────────────────────────────────
# PERSONAS
# ─────────────────────────────────────────────────────────────────────────────

def listar_personas():
    return ejecutar_query("SELECT * FROM persona ORDER BY apellido, primer_nombre")


def obtener_persona(id_persona: int):
    return ejecutar_query(
        "SELECT * FROM persona WHERE id_persona = %s",
        (id_persona,), fetchone=True
    )


def crear_persona(primer_nombre: str, apellido: str, documento_identidad: str,
                  segundo_nombre: str = None, segundo_apellido: str = None,
                  telefono: str = None, correo: str = None):
    if ejecutar_query(
        "SELECT id_persona FROM persona WHERE documento_identidad = %s",
        (documento_identidad,), fetchone=True
    ):
        return False, "Ya existe una persona con ese documento de identidad."

    id_nuevo = ejecutar_comando(
        """INSERT INTO persona
           (primer_nombre, segundo_nombre, apellido, segundo_apellido,
            documento_identidad, telefono, correo)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (primer_nombre, segundo_nombre, apellido, segundo_apellido,
         documento_identidad, telefono, correo)
    )
    return True, id_nuevo


def actualizar_persona(id_persona: int, **kwargs):
    if not obtener_persona(id_persona):
        return False, "Persona no encontrada."

    campos_permitidos = {
        "primer_nombre", "segundo_nombre", "apellido", "segundo_apellido",
        "telefono", "correo"
    }
    campos, valores = [], []
    for campo, valor in kwargs.items():
        if campo in campos_permitidos and valor is not None:
            campos.append(f"{campo} = %s"); valores.append(valor)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_persona)
    ejecutar_comando(
        f"UPDATE persona SET {', '.join(campos)} WHERE id_persona = %s",
        tuple(valores)
    )
    return True, "Persona actualizada."


def eliminar_persona(id_persona: int):
    """Elimina la persona sólo si no tiene usuario asociado."""
    if ejecutar_query(
        "SELECT id_usuario FROM usuario WHERE id_persona = %s LIMIT 1",
        (id_persona,), fetchone=True
    ):
        return False, "No se puede eliminar: la persona tiene un usuario asociado."
    ejecutar_comando("DELETE FROM persona WHERE id_persona = %s", (id_persona,))
    return True, "Persona eliminada."


# ─────────────────────────────────────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────────────────────────────────────

def listar_usuarios():
    return ejecutar_query(
        """SELECT u.id_usuario, u.username, u.correo, u.activo, u.id_persona, u.id_rol,
                  r.nombre AS nombre_rol,
                  p.primer_nombre, p.segundo_nombre, p.apellido, p.segundo_apellido,
                  p.documento_identidad
           FROM usuario u
           JOIN rol r ON u.id_rol = r.id_rol
           JOIN persona p ON u.id_persona = p.id_persona
           ORDER BY u.username"""
    )


def obtener_usuario(id_usuario: int):
    return ejecutar_query(
        """SELECT u.*, r.nombre AS rol,
                  CONCAT(p.primer_nombre,' ',COALESCE(p.segundo_nombre,''),' ',
                         p.apellido,' ',COALESCE(p.segundo_apellido,'')) AS nombre_persona
           FROM usuario u
           JOIN rol r ON u.id_rol = r.id_rol
           JOIN persona p ON u.id_persona = p.id_persona
           WHERE u.id_usuario = %s""",
        (id_usuario,), fetchone=True
    )


def crear_usuario(username: str, password_plain: str, correo: str,
                  id_persona: int, id_rol: int):
    """
    Crea un usuario con la contraseña hasheada.
    Valida que username sea único y que persona/rol existan.
    """
    username = username.strip().lower()

    if ejecutar_query(
        "SELECT id_usuario FROM usuario WHERE username = %s", (username,), fetchone=True
    ):
        return False, f"El nombre de usuario '{username}' ya está en uso."

    if not ejecutar_query(
        "SELECT id_persona FROM persona WHERE id_persona = %s", (id_persona,), fetchone=True
    ):
        return False, "La persona indicada no existe."

    if not ejecutar_query(
        "SELECT id_rol FROM rol WHERE id_rol = %s", (id_rol,), fetchone=True
    ):
        return False, "El rol indicado no existe."

    # Verifica que la persona no tenga ya un usuario
    if ejecutar_query(
        "SELECT id_usuario FROM usuario WHERE id_persona = %s LIMIT 1",
        (id_persona,), fetchone=True
    ):
        return False, "Esta persona ya tiene un usuario asignado."

    id_nuevo = ejecutar_comando(
        """INSERT INTO usuario (username, password_hash, correo, id_persona, id_rol)
           VALUES (%s, %s, %s, %s, %s)""",
        (username, _hash_password(password_plain), correo, id_persona, id_rol)
    )
    return True, id_nuevo


def actualizar_usuario(id_usuario: int, **kwargs):
    """
    Actualiza campos del usuario.
    Campos permitidos: correo, activo, id_rol.
    No permite cambiar username ni password aquí (hay función aparte para password).
    """
    if not obtener_usuario(id_usuario):
        return False, "Usuario no encontrado."

    campos_permitidos = {"correo", "activo", "id_rol"}
    campos, valores = [], []
    for campo, valor in kwargs.items():
        if campo in campos_permitidos and valor is not None:
            campos.append(f"{campo} = %s"); valores.append(valor)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_usuario)
    ejecutar_comando(
        f"UPDATE usuario SET {', '.join(campos)} WHERE id_usuario = %s",
        tuple(valores)
    )
    return True, "Usuario actualizado."


def cambiar_password(id_usuario: int, password_actual: str, password_nueva: str):
    """Cambia la contraseña verificando la actual."""
    usuario = ejecutar_query(
        "SELECT password_hash FROM usuario WHERE id_usuario = %s",
        (id_usuario,), fetchone=True
    )
    if not usuario:
        return False, "Usuario no encontrado."
    if usuario["password_hash"] != _hash_password(password_actual):
        return False, "La contraseña actual es incorrecta."
    if len(password_nueva) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres."

    ejecutar_comando(
        "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s",
        (_hash_password(password_nueva), id_usuario)
    )
    return True, "Contraseña actualizada correctamente."


def reset_password(id_usuario: int, password_nueva: str):
    """
    Resetea la contraseña sin verificar la anterior.
    Solo debe llamarse desde rutas protegidas con rol ADMINISTRADOR.
    """
    if not obtener_usuario(id_usuario):
        return False, "Usuario no encontrado."
    ejecutar_comando(
        "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s",
        (_hash_password(password_nueva), id_usuario)
    )
    return True, "Contraseña reseteada correctamente."


def desactivar_usuario(id_usuario: int):
    """Borrado lógico del usuario."""
    if not obtener_usuario(id_usuario):
        return False, "Usuario no encontrado."
    ejecutar_comando(
        "UPDATE usuario SET activo = FALSE WHERE id_usuario = %s", (id_usuario,)
    )
    return True, "Usuario desactivado."


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN / SESIÓN
# ─────────────────────────────────────────────────────────────────────────────

def login(username: str, password_plain: str):
    """
    Verifica credenciales y, si son correctas, guarda el usuario en la sesión Flask.
    Devuelve (True, dict_usuario) o (False, mensaje_error).
    """
    usuario = ejecutar_query(
        """SELECT u.id_usuario, u.username, u.correo, u.activo,
                  r.id_rol, r.nombre AS rol
           FROM usuario u
           JOIN rol r ON u.id_rol = r.id_rol
           WHERE u.username = %s AND u.password_hash = %s""",
        (username.strip().lower(), _hash_password(password_plain)),
        fetchone=True
    )

    if not usuario:
        return False, "Credenciales incorrectas."
    if not usuario["activo"]:
        return False, "El usuario está desactivado. Contacte al administrador."

    # Guardar en sesión
    session["usuario_id"]  = usuario["id_usuario"]
    session["usuario_name"] = usuario["username"]
    session["usuario_rol"]  = usuario["rol"]
    session["id_rol"]       = usuario["id_rol"]

    return True, {
        "id_usuario": usuario["id_usuario"],
        "username":   usuario["username"],
        "correo":     usuario["correo"],
        "rol":        usuario["rol"]
    }


def logout():
    session.clear()
    return True, "Sesión cerrada."


def usuario_activo():
    """Devuelve la info básica del usuario en sesión, o None si no hay sesión."""
    if "usuario_id" not in session:
        return None
    return {
        "id_usuario":  session["usuario_id"],
        "username":    session["usuario_name"],
        "rol":         session["usuario_rol"],
        "id_rol":      session["id_rol"]
    }


# ─────────────────────────────────────────────────────────────────────────────
# MENÚS
# ─────────────────────────────────────────────────────────────────────────────

def listar_menus():
    """Devuelve todos los menús en forma de lista plana."""
    return ejecutar_query(
        """SELECT m.*, mp.nombre AS nombre_padre
           FROM menu m
           LEFT JOIN menu mp ON m.id_menu_padre = mp.id_menu
           ORDER BY COALESCE(m.id_menu_padre, m.id_menu), m.id_menu"""
    )


def menus_del_rol(id_rol: int):
    """
    Devuelve los menús asignados a un rol.
    El ADMINISTRADOR (id_rol cuyo nombre='ADMINISTRADOR') recibe todos los menús.
    """
    rol = obtener_rol(id_rol)
    if rol and rol["nombre"] == "ADMINISTRADOR":
        return ejecutar_query("SELECT * FROM menu ORDER BY id_menu")

    return ejecutar_query(
        """SELECT m.*
           FROM menu m
           JOIN rol_menu rm ON m.id_menu = rm.id_menu
           WHERE rm.id_rol = %s
           ORDER BY m.id_menu""",
        (id_rol,)
    )


def arbol_menus(id_rol: int = None):
    """
    Devuelve los menús como árbol jerárquico (lista de raíces con hijos anidados).
    Si se pasa id_rol, filtra sólo los menús de ese rol.
    """
    menus = menus_del_rol(id_rol) if id_rol else listar_menus()
    por_id = {m["id_menu"]: {**m, "hijos": []} for m in menus}
    raices = []
    for m in por_id.values():
        padre = m.get("id_menu_padre")
        if padre and padre in por_id:
            por_id[padre]["hijos"].append(m)
        else:
            raices.append(m)
    return raices


def crear_menu(nombre: str, ruta: str = None, id_menu_padre: int = None):
    if id_menu_padre:
        if not ejecutar_query(
            "SELECT id_menu FROM menu WHERE id_menu = %s", (id_menu_padre,), fetchone=True
        ):
            return False, "El menú padre indicado no existe."

    id_nuevo = ejecutar_comando(
        "INSERT INTO menu (nombre, ruta, id_menu_padre) VALUES (%s, %s, %s)",
        (nombre, ruta, id_menu_padre)
    )
    return True, id_nuevo


def actualizar_menu(id_menu: int, nombre: str = None, ruta: str = None,
                    id_menu_padre: int = None):
    if not ejecutar_query(
        "SELECT id_menu FROM menu WHERE id_menu = %s", (id_menu,), fetchone=True
    ):
        return False, "Menú no encontrado."

    campos, valores = [], []
    if nombre:      campos.append("nombre = %s");        valores.append(nombre)
    if ruta:        campos.append("ruta = %s");          valores.append(ruta)
    if id_menu_padre is not None:
        campos.append("id_menu_padre = %s"); valores.append(id_menu_padre or None)

    if not campos:
        return False, "No se proporcionaron datos para actualizar."

    valores.append(id_menu)
    ejecutar_comando(
        f"UPDATE menu SET {', '.join(campos)} WHERE id_menu = %s", tuple(valores)
    )
    return True, "Menú actualizado."


def eliminar_menu(id_menu: int):
    ejecutar_comando("DELETE FROM rol_menu WHERE id_menu = %s", (id_menu,))
    ejecutar_comando("DELETE FROM menu WHERE id_menu = %s", (id_menu,))
    return True, "Menú eliminado."


# ─────────────────────────────────────────────────────────────────────────────
# ROL ↔ MENÚ
# ─────────────────────────────────────────────────────────────────────────────

def asignar_menu_a_rol(id_rol: int, id_menu: int):
    if ejecutar_query(
        "SELECT 1 FROM rol_menu WHERE id_rol=%s AND id_menu=%s",
        (id_rol, id_menu), fetchone=True
    ):
        return False, "El menú ya está asignado a ese rol."
    ejecutar_comando(
        "INSERT INTO rol_menu (id_rol, id_menu) VALUES (%s, %s)", (id_rol, id_menu)
    )
    return True, "Menú asignado al rol."


def quitar_menu_de_rol(id_rol: int, id_menu: int):
    ejecutar_comando(
        "DELETE FROM rol_menu WHERE id_rol=%s AND id_menu=%s", (id_rol, id_menu)
    )
    return True, "Menú quitado del rol."


def menus_asignados_al_rol(id_rol: int):
    return ejecutar_query(
        """SELECT m.*
           FROM menu m
           JOIN rol_menu rm ON m.id_menu = rm.id_menu
           WHERE rm.id_rol = %s
           ORDER BY m.id_menu""",
        (id_rol,)
    )


# ─────────────────────────────────────────────────────────────────────────────
# DECORADOR DE PROTECCIÓN DE RUTAS
# ─────────────────────────────────────────────────────────────────────────────

def requiere_rol(*roles_permitidos):
    """
    Decorador para proteger endpoints por rol.

    Uso:
        @requiere_rol("ADMINISTRADOR", "SUPERVISOR")
        def mi_ruta():
            ...

    Si no hay sesión activa → 401 Unauthorized
    Si el rol no tiene permiso → 403 Forbidden
    El ADMINISTRADOR siempre tiene acceso.
    """
    from flask import jsonify

    def decorador(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            u = usuario_activo()
            if not u:
                return jsonify({"error": "No autenticado. Inicie sesión."}), 401
            if u["rol"] == "ADMINISTRADOR" or u["rol"] in roles_permitidos:
                return f(*args, **kwargs)
            return jsonify({
                "error": f"Acceso denegado. Se requiere uno de los roles: {', '.join(roles_permitidos)}"
            }), 403
        return wrapper
    return decorador
