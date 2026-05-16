"""
routes/estudiante.py - Rutas de Estudiantes
"""
from flask import Blueprint, request, jsonify
from logic.estudiante import (listar_estudiantes, obtener_estudiante, crear_estudiante,
                               actualizar_estudiante, desactivar_estudiante, buscar_por_codigo)

estudiante_bp = Blueprint("estudiante", __name__)

@estudiante_bp.route("/", methods=["GET"])
def get_estudiantes():
    """Retorna lista de estudiantes desde BD."""
    id_programa = request.args.get("id_programa", type=int)
    return jsonify(listar_estudiantes(id_programa=id_programa)), 200

@estudiante_bp.route("/<int:id_estudiante>", methods=["GET"])
def get_estudiante(id_estudiante):
    """Retorna un estudiante por ID desde BD."""
    est = obtener_estudiante(id_estudiante)
    if not est:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(est), 200

@estudiante_bp.route("/codigo/<codigo>", methods=["GET"])
def get_por_codigo(codigo):
    """Retorna un estudiante por código desde BD."""
    e = buscar_por_codigo(codigo)
    if not e:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(e), 200

@estudiante_bp.route("/", methods=["POST"])
def post_estudiante():
    """Crea un estudiante en BD."""
    d = request.json or {}
    requeridos = ("codigo_estudiantil", "documento_identidad",
                  "primer_nombre", "apellido", "id_programa", "id_pensum")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(requeridos)}"}), 400

    exito, resultado = crear_estudiante(
        d["codigo_estudiantil"], d["documento_identidad"],
        d["primer_nombre"], d["apellido"],
        d["id_programa"], d["id_pensum"],
        segundo_nombre=d.get("segundo_nombre"),
        segundo_apellido=d.get("segundo_apellido"),
        correo=d.get("correo"),
        telefono=d.get("telefono")
    )
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Estudiante creado", "id_estudiante": resultado}), 201

@estudiante_bp.route("/<int:id_estudiante>", methods=["PUT"])
def put_estudiante(id_estudiante):
    """Actualiza un estudiante en BD."""
    d = request.json or {}
    campos_validos = {"primer_nombre", "segundo_nombre", "apellido", "segundo_apellido",
                      "correo", "telefono", "activo", "id_programa", "id_pensum"}
    kwargs = {k: v for k, v in d.items() if k in campos_validos}
    exito, msg = actualizar_estudiante(id_estudiante, **kwargs)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

@estudiante_bp.route("/<int:id_estudiante>", methods=["DELETE"])
def delete_estudiante(id_estudiante):
    """Elimina (desactiva) un estudiante en BD."""
    exito, msg = desactivar_estudiante(id_estudiante)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200

