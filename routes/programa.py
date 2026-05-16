"""
routes/programa.py - Rutas de Programas Académicos
"""
from flask import Blueprint, request, jsonify
from logic.programa import (listar_programas, obtener_programa, crear_programa,
                             actualizar_programa, eliminar_programa)

programa_bp = Blueprint("programa", __name__)

# ── Programas ─────────────────────────────────────────────────

@programa_bp.route("/", methods=["GET"])
def get_programas():
    """Retorna lista de programas desde BD."""
    solo_activos = request.args.get("activos", "true").lower() == "true"
    return jsonify(listar_programas(solo_activos)), 200

@programa_bp.route("/<int:id_programa>", methods=["GET"])
def get_programa(id_programa):
    """Retorna un programa por ID desde BD."""
    prog = obtener_programa(id_programa)
    if not prog:
        return jsonify({"error": "Programa no encontrado"}), 404
    return jsonify(prog), 200

@programa_bp.route("/", methods=["POST"])
def post_programa():
    """Crea un programa en BD."""
    d = request.json or {}
    if not d.get("codigo") or not d.get("nombre") or not d.get("nivel"):
        return jsonify({"error": "Se requieren código, nombre y nivel"}), 400
    exito, resultado = crear_programa(d["codigo"], d["nombre"], d["nivel"])
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Programa creado", "id_programa": resultado}), 201

@programa_bp.route("/<int:id_programa>", methods=["PUT"])
def put_programa(id_programa):
    """Actualiza un programa en BD."""
    d = request.json or {}
    exito, msg = actualizar_programa(id_programa,
                                     nombre=d.get("nombre"),
                                     nivel=d.get("nivel"),
                                     activo=d.get("activo"))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@programa_bp.route("/<int:id_programa>", methods=["DELETE"])
def delete_programa(id_programa):
    """Elimina (desactiva) un programa en BD."""
    exito, msg = eliminar_programa(id_programa)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

