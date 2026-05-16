"""routes/pensum.py - Rutas de Pensum"""
from flask import Blueprint, request, jsonify
from logic.pensum import (listar_pensum_programa, obtener_pensum, crear_pensum,
                          actualizar_pensum, eliminar_pensum)

pensum_bp = Blueprint("pensum", __name__)

@pensum_bp.route("/programa/<int:id_programa>", methods=["GET"])
def get_pensum_programa(id_programa):
    """Retorna lista de pensumes de un programa."""
    return jsonify(listar_pensum_programa(id_programa)), 200

@pensum_bp.route("/<int:id_pensum>", methods=["GET"])
def get_pensum(id_pensum):
    """Retorna un pensum por ID."""
    p = obtener_pensum(id_pensum)
    if not p:
        return jsonify({"error": "Pensum no encontrado"}), 404
    return jsonify(p), 200

@pensum_bp.route("/", methods=["POST"])
def post_pensum():
    """Crea un pensum."""
    d = request.json or {}
    requeridos = ("id_programa", "version", "total_semestres", "fecha_vigencia")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Se requieren: {', '.join(requeridos)}"}), 400
    
    exito, resultado = crear_pensum(
        d["id_programa"], d["version"], 
        int(d["total_semestres"]), d["fecha_vigencia"]
    )
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Pensum creado", "id_pensum": resultado}), 201

@pensum_bp.route("/<int:id_pensum>", methods=["PUT"])
def put_pensum(id_pensum):
    """Actualiza un pensum."""
    d = request.json or {}
    campos = {}
    if "version" in d:
        campos["version"] = d["version"]
    if "total_semestres" in d:
        campos["total_semestres"] = int(d["total_semestres"])
    if "fecha_vigencia" in d:
        campos["fecha_vigencia"] = d["fecha_vigencia"]
    
    exito, msg = actualizar_pensum(id_pensum, **campos)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@pensum_bp.route("/<int:id_pensum>", methods=["DELETE"])
def delete_pensum(id_pensum):
    """Elimina un pensum."""
    exito, msg = eliminar_pensum(id_pensum)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200
