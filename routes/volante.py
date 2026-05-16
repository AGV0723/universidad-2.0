"""routes/volante.py"""
from flask import Blueprint, request, jsonify
from logic.volante import obtener_volante, listar_volantes, obtener_volante_estudiante_periodo, contar_volantes_periodo

volante_bp = Blueprint("volante", __name__)

@volante_bp.route("/", methods=["GET"])
def get_volantes():
    """Retorna lista de volantes desde BD."""
    id_periodo = request.args.get("id_periodo", type=int)
    id_programa = request.args.get("id_programa", type=int)
    id_estudiante = request.args.get("id_estudiante", type=int)
    
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    
    return jsonify(listar_volantes(id_periodo, id_programa, id_estudiante)), 200

@volante_bp.route("/<int:id_volante>", methods=["GET"])
def get_volante(id_volante):
    """Retorna un volante por ID desde BD."""
    volante = obtener_volante(id_volante)
    if not volante:
        return jsonify({"error": "Volante no encontrado"}), 404
    return jsonify(volante), 200

@volante_bp.route("/estudiante/<int:id_estudiante>/periodo/<int:id_periodo>", methods=["GET"])
def get_volante_estudiante(id_estudiante, id_periodo):
    """Retorna volante de un estudiante en un período."""
    volante = obtener_volante_estudiante_periodo(id_estudiante, id_periodo)
    if not volante:
        return jsonify({"error": "No hay volante para este estudiante en este período"}), 404
    return jsonify(volante), 200

@volante_bp.route("/contar/<int:id_periodo>", methods=["GET"])
def get_contar_volantes(id_periodo):
    """Retorna cantidad de volantes en un período."""
    count = contar_volantes_periodo(id_periodo)
    return jsonify({"id_periodo": id_periodo, "cantidad": count}), 200

@volante_bp.route("/periodo/<int:id_periodo>/estadisticas", methods=["GET"])
def get_estadisticas_volantes(id_periodo):
    """Retorna estadísticas de volantes generados en un período."""
    total = contar_volantes_periodo(id_periodo)
    return jsonify({"id_periodo": id_periodo, "total_volantes": total})