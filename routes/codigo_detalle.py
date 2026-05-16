"""routes/codigo_detalle.py"""
from flask import Blueprint, request, jsonify
from logic.codigo_detalle import (
    listar_codigos, obtener_codigo, obtener_codigo_por_codigo,
    crear_codigo, actualizar_codigo, eliminar_codigo
)

codigo_detalle_bp = Blueprint("codigo_detalle", __name__)

@codigo_detalle_bp.route("/", methods=["GET"])
def get_codigos():
    """Retorna lista de códigos desde BD."""
    grupo = request.args.get("grupo")
    return jsonify(listar_codigos(grupo)), 200

@codigo_detalle_bp.route("/<int:id_codigo>", methods=["GET"])
def get_codigo_by_id(id_codigo):
    """Retorna un código por ID desde BD."""
    cod = obtener_codigo(id_codigo)
    if not cod:
        return jsonify({"error": "Código no encontrado"}), 404
    return jsonify(cod), 200

@codigo_detalle_bp.route("/codigo/<codigo>", methods=["GET"])
def get_por_codigo_str(codigo):
    """Retorna un código por su código desde BD."""
    cod = obtener_codigo_por_codigo(codigo)
    if not cod:
        return jsonify({"error": "Código no encontrado"}), 404
    return jsonify(cod), 200

@codigo_detalle_bp.route("/", methods=["POST"])
def post_codigo():
    """Crea un nuevo código de detalle."""
    d = request.json
    if not d or not all(k in d for k in ("codigo", "descripcion", "grupo")):
        return jsonify({"error": "Faltan campos requeridos: codigo, descripcion, grupo"}), 400
    
    exito, resultado = crear_codigo(d["codigo"], d["descripcion"], d["grupo"])
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Código de detalle creado", "id_codigo": resultado}), 201

@codigo_detalle_bp.route("/<int:id_codigo>", methods=["PUT"])
def put_codigo(id_codigo):
    """Actualiza un código de detalle existente."""
    d = request.json or {}
    exito, msg = actualizar_codigo(id_codigo,
                                   descripcion=d.get("descripcion"),
                                   grupo=d.get("grupo"))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg})

@codigo_detalle_bp.route("/<int:id_codigo>", methods=["DELETE"])
def delete_codigo(id_codigo):
    """Elimina un código de detalle."""
    exito, msg = eliminar_codigo(id_codigo)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg})
