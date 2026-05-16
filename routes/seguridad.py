"""
routes/seguridad.py - Rutas de Autenticación y Seguridad
"""
from flask import Blueprint, request, jsonify, session, render_template, redirect
from logic.seguridad import (
    login, logout, usuario_activo,
    listar_roles, obtener_rol, crear_rol, actualizar_rol, eliminar_rol,
    listar_personas, obtener_persona, crear_persona, actualizar_persona, eliminar_persona,
    listar_usuarios, obtener_usuario, crear_usuario, actualizar_usuario, desactivar_usuario,
    cambiar_password, reset_password,
    listar_menus, menus_del_rol
)

seguridad_bp = Blueprint("seguridad", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

@seguridad_bp.route("/login", methods=["GET"])
def get_login():
    """Muestra la página de login."""
    return render_template("login.html")

@seguridad_bp.route("/login", methods=["POST"])
def post_login():
    """Login con credenciales desde BD."""
    d = request.json or request.form or {}
    username = d.get("username", "").strip()
    password = d.get("password", "").strip()
    
    if not username or not password:
        if request.json:
            return jsonify({"error": "Usuario y contraseña requeridos"}), 400
        return render_template("login.html", error="Usuario y contraseña requeridos")
    
    exito, resultado = login(username, password)
    if not exito:
        if request.json:
            return jsonify({"error": resultado}), 401
        return render_template("login.html", error=resultado)
    
    if request.json:
        return jsonify({"mensaje": "Bienvenido", "usuario": resultado}), 200
    return redirect("/")

@seguridad_bp.route("/logout", methods=["POST", "GET"])
def post_logout():
    """Cierra la sesión."""
    logout()
    if request.json:
        return jsonify({"mensaje": "Sesión cerrada"}), 200
    return redirect("/seguridad/login")

@seguridad_bp.route("/sesion", methods=["GET"])
def get_sesion():
    """Retorna información de la sesión actual."""
    u = usuario_activo()
    if not u:
        return jsonify({"error": "No hay sesión activa"}), 401
    return jsonify(u), 200

@seguridad_bp.route("/menus/mi-rol", methods=["GET"])
def get_menus_mi_rol():
    """Retorna menús disponibles para el usuario en sesión."""
    u = usuario_activo()
    if not u:
        return jsonify({"error": "No autenticado"}), 401
    return jsonify(menus_del_rol(u["id_rol"])), 200

# ─────────────────────────────────────────────────────────────────────────────
# ROLES (solo ADMINISTRADOR)
# ─────────────────────────────────────────────────────────────────────────────

@seguridad_bp.route("/roles", methods=["GET"])
def get_roles():
    """Listar todos los roles."""
    return jsonify(listar_roles()), 200

@seguridad_bp.route("/roles/<int:id_rol>", methods=["GET"])
def get_rol(id_rol):
    """Obtener un rol específico."""
    r = obtener_rol(id_rol)
    if not r:
        return jsonify({"error": "Rol no encontrado"}), 404
    return jsonify(r), 200

@seguridad_bp.route("/roles", methods=["POST"])
def post_rol():
    """Crear un rol."""
    d = request.json or {}
    if not d.get("nombre"):
        return jsonify({"error": "Nombre requerido"}), 400
    exito, resultado = crear_rol(d["nombre"], d.get("descripcion"))
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Rol creado", "id_rol": resultado}), 201

@seguridad_bp.route("/roles/<int:id_rol>", methods=["PUT"])
def put_rol(id_rol):
    """Actualizar un rol."""
    d = request.json or {}
    exito, msg = actualizar_rol(id_rol, d.get("nombre"), d.get("descripcion"))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@seguridad_bp.route("/roles/<int:id_rol>", methods=["DELETE"])
def delete_rol(id_rol):
    """Eliminar un rol."""
    exito, msg = eliminar_rol(id_rol)
    if not exito:
        return jsonify({"error": msg}), 409
    return jsonify({"mensaje": msg}), 200

# ─────────────────────────────────────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────────────────────────────────────

@seguridad_bp.route("/usuarios", methods=["GET"])
def get_usuarios():
    """Listar usuarios."""
    return jsonify(listar_usuarios()), 200

@seguridad_bp.route("/usuarios/<int:id_usuario>", methods=["GET"])
def get_usuario(id_usuario):
    """Obtener usuario específico."""
    u = obtener_usuario(id_usuario)
    if not u:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(u), 200

@seguridad_bp.route("/usuarios", methods=["POST"])
def post_usuario():
    """Crear usuario."""
    d = request.json or {}
    requeridos = ("username", "password", "correo", "id_persona", "id_rol")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Campos requeridos: {', '.join(requeridos)}"}), 400
    exito, resultado = crear_usuario(d["username"], d["password"], d["correo"],
                                      int(d["id_persona"]), int(d["id_rol"]))
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Usuario creado", "id_usuario": resultado}), 201

@seguridad_bp.route("/usuarios/<int:id_usuario>", methods=["PUT"])
def put_usuario(id_usuario):
    """Actualizar usuario."""
    d = request.json or {}
    campos = {k: d[k] for k in ("correo", "activo", "id_rol") if k in d}
    exito, msg = actualizar_usuario(id_usuario, **campos)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@seguridad_bp.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
def delete_usuario(id_usuario):
    """Desactivar usuario."""
    exito, msg = desactivar_usuario(id_usuario)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@seguridad_bp.route("/usuarios/<int:id_usuario>/password", methods=["PUT"])
def put_reset_password(id_usuario):
    """Resetear contraseña (admin only)."""
    d = request.json or {}
    if not d.get("password_nueva"):
        return jsonify({"error": "password_nueva requerida"}), 400
    exito, msg = reset_password(id_usuario, d["password_nueva"])
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@seguridad_bp.route("/mi-password", methods=["PUT"])
def put_cambiar_mi_password():
    """Cambiar mi propia contraseña."""
    u = usuario_activo()
    if not u:
        return jsonify({"error": "No autenticado"}), 401
    d = request.json or {}
    if not d.get("password_actual") or not d.get("password_nueva"):
        return jsonify({"error": "password_actual y password_nueva requeridas"}), 400
    exito, msg = cambiar_password(u["id_usuario"], d["password_actual"], d["password_nueva"])
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200


# ─────────────────────────────────────────────────────────────────────────────
# PERSONAS
# ─────────────────────────────────────────────────────────────────────────────

@seguridad_bp.route("/personas", methods=["GET"])
def get_personas():
    """Listar todas las personas."""
    return jsonify(listar_personas()), 200

@seguridad_bp.route("/personas/<int:id_persona>", methods=["GET"])
def get_persona(id_persona):
    """Obtener persona específica."""
    p = obtener_persona(id_persona)
    if not p:
        return jsonify({"error": "Persona no encontrada"}), 404
    return jsonify(p), 200

@seguridad_bp.route("/personas", methods=["POST"])
def post_persona():
    """Crear persona."""
    d = request.json or {}
    requeridos = ("primer_nombre", "apellido", "documento_identidad")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Campos requeridos: {', '.join(requeridos)}"}), 400
    exito, resultado = crear_persona(
        d["primer_nombre"],
        d["apellido"],
        d["documento_identidad"],
        segundo_nombre=d.get("segundo_nombre"),
        segundo_apellido=d.get("segundo_apellido"),
        telefono=d.get("telefono"),
        correo=d.get("correo")
    )
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Persona creada", "id_persona": resultado}), 201

@seguridad_bp.route("/personas/<int:id_persona>", methods=["PUT"])
def put_persona(id_persona):
    """Actualizar persona."""
    d = request.json or {}
    campos = {k: d[k] for k in ("primer_nombre", "segundo_nombre", "apellido", "segundo_apellido", 
                                  "documento_identidad", "telefono", "correo") if k in d}
    exito, msg = actualizar_persona(id_persona, **campos)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@seguridad_bp.route("/personas/<int:id_persona>", methods=["DELETE"])
def delete_persona(id_persona):
    """Eliminar persona."""
    exito, msg = eliminar_persona(id_persona)
    if not exito:
        return jsonify({"error": msg}), 409
    return jsonify({"mensaje": msg}), 200


# ─────────────────────────────────────────────────────────────────────────────
# MENÚS (solo ADMINISTRADOR)
# ─────────────────────────────────────────────────────────────────────────────

@seguridad_bp.route("/menus", methods=["GET"])
def get_menus():
    """Listar todos los menús."""
    return jsonify(listar_menus()), 200

@seguridad_bp.route("/menus/rol/<int:id_rol>", methods=["GET"])
def get_menus_rol(id_rol):
    """Obtener menús asignados a un rol."""
    return jsonify(menus_del_rol(id_rol)), 200

@seguridad_bp.route("/menus/rol/<int:id_rol>/<int:id_menu>", methods=["POST"])
def post_menu_rol(id_rol, id_menu):
    """Asignar menú a un rol."""
    from logic.seguridad import asignar_menu_a_rol
    exito, msg = asignar_menu_a_rol(id_rol, id_menu)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 201

@seguridad_bp.route("/menus/rol/<int:id_rol>/<int:id_menu>", methods=["DELETE"])
def delete_menu_rol(id_rol, id_menu):
    """Quitar menú de un rol."""
    from logic.seguridad import quitar_menu_de_rol
    exito, msg = quitar_menu_de_rol(id_rol, id_menu)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200
