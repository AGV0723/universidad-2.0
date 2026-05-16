"""routes/inscripcion.py"""
from flask import Blueprint, request, jsonify
inscripcion_bp = Blueprint("inscripcion", __name__)

@inscripcion_bp.route("/", methods=["GET"])
def get_inscripciones():
    return jsonify([
        {"id": 1, "estudiante": "Juan Pérez", "periodo": "2024-1", "estado": "ACTIVA"},
        {"id": 2, "estudiante": "María López", "periodo": "2024-1", "estado": "ACTIVA"},
    ]), 200

@inscripcion_bp.route("/<int:id_insc>", methods=["GET"])
def get_inscripcion(id_insc):
    return jsonify({"id": id_insc, "estudiante": "Juan Pérez", "periodo": "2024-1"}), 200

@inscripcion_bp.route("/", methods=["POST"])
def post_inscripcion():
    return jsonify({"mensaje": "Inscripción creada", "id": 99}), 201

@inscripcion_bp.route("/<int:id_insc>", methods=["PUT"])
def put_inscripcion(id_insc):
    return jsonify({"mensaje": "Inscripción actualizada"}), 200

@inscripcion_bp.route("/<int:id_insc>", methods=["DELETE"])
def delete_inscripcion(id_insc):
    return jsonify({"mensaje": "Inscripción eliminada"}), 200
