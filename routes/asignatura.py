"""routes/asignatura.py - Rutas de Asignaturas"""
from flask import Blueprint, request, jsonify
from logic.asignatura import (listar_asignaturas, obtener_asignatura, crear_asignatura,
                               actualizar_asignatura, eliminar_asignatura,
                               listar_asignaturas_pensum, agregar_asignatura_pensum,
                               quitar_asignatura_pensum)

asignatura_bp = Blueprint("asignatura", __name__)

@asignatura_bp.route("/", methods=["GET"])
def get_asignaturas():
    """Retorna lista de asignaturas desde BD."""
    return jsonify(listar_asignaturas()), 200

@asignatura_bp.route("/<int:id_asignatura>", methods=["GET"])
def get_asignatura(id_asignatura):
    """Retorna una asignatura por ID desde BD."""
    a = obtener_asignatura(id_asignatura)
    if not a:
        return jsonify({"error": "Asignatura no encontrada"}), 404
    return jsonify(a), 200

@asignatura_bp.route("/", methods=["POST"])
def post_asignatura():
    """Crea una asignatura en BD."""
    d = request.json or {}
    if not all(d.get(k) for k in ("codigo", "nombre", "creditos")):
        return jsonify({"error": "Faltan campos: codigo, nombre, creditos"}), 400
    exito, resultado = crear_asignatura(d["codigo"], d["nombre"], int(d["creditos"]))
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Asignatura creada", "id_asignatura": resultado}), 201

@asignatura_bp.route("/<int:id_asignatura>", methods=["PUT"])
def put_asignatura(id_asignatura):
    """Actualiza una asignatura en BD."""
    d = request.json or {}
    exito, msg = actualizar_asignatura(id_asignatura,
                                       nombre=d.get("nombre"),
                                       creditos=d.get("creditos"))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@asignatura_bp.route("/<int:id_asignatura>", methods=["DELETE"])
def delete_asignatura(id_asignatura):
    """Elimina una asignatura en BD."""
    exito, msg = eliminar_asignatura(id_asignatura)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200


# ── Pensum-Asignatura ──────────────────────────────────────────
@asignatura_bp.route("/pensum/<int:id_pensum>/plan", methods=["GET"])
def get_plan_pensum(id_pensum):
    """Retorna asignaturas de un pensum."""
    return jsonify(listar_asignaturas_pensum(id_pensum)), 200

@asignatura_bp.route("/pensum/<int:id_pensum>", methods=["POST"])
def post_asignatura_pensum(id_pensum):
    """Agrega una asignatura a un pensum."""
    d = request.json or {}
    if not d.get("id_asignatura") or "semestre" not in d:
        return jsonify({"error": "Se requieren id_asignatura y semestre"}), 400
    
    exito, msg = agregar_asignatura_pensum(
        id_pensum, 
        d["id_asignatura"], 
        int(d["semestre"]),
        d.get("obligatoria", True)
    )
    if not exito:
        return jsonify({"error": msg}), 409
    return jsonify({"mensaje": msg}), 201

@asignatura_bp.route("/pensum/<int:id_pensum>/<int:id_asignatura>", methods=["DELETE"])
def delete_asignatura_pensum(id_pensum, id_asignatura):
    """Quita una asignatura de un pensum."""
    exito, msg = quitar_asignatura_pensum(id_pensum, id_asignatura)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

