"""routes/regla_cobro.py"""
from flask import Blueprint, request, jsonify
from logic.regla_cobro import (listar_reglas, obtener_regla, crear_regla,
                               actualizar_regla, eliminar_regla)

regla_bp = Blueprint("regla", __name__)

@regla_bp.route("/", methods=["GET"])
def get_reglas():
    """Retorna lista de reglas desde BD."""
    id_periodo = request.args.get("id_periodo", type=int)
    id_programa = request.args.get("id_programa", type=int)
    return jsonify(listar_reglas(id_periodo, id_programa)), 200

@regla_bp.route("/<int:id_regla>", methods=["GET"])
def get_regla(id_regla):
    """Retorna una regla por ID desde BD."""
    r = obtener_regla(id_regla)
    if not r:
        return jsonify({"error": "Regla no encontrada"}), 404
    return jsonify(r), 200

@regla_bp.route("/", methods=["POST"])
def post_regla():
    """Crea una regla en BD."""
    d = request.json or {}
    requeridos = ("modalidad", "valor", "id_periodo", "id_programa")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Se requieren: {', '.join(requeridos)}"}), 400
    
    exito, resultado = crear_regla(d["modalidad"], float(d["valor"]),
                                   int(d["id_periodo"]), int(d["id_programa"]))
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Regla creada", "id_regla": resultado}), 201


@regla_bp.route("/<int:id_regla>", methods=["PUT"])
def put_regla(id_regla):
    d = request.json or {}
    if "valor" not in d:
        return jsonify({"error": "Se requiere 'valor'"}), 400
    exito, msg = actualizar_regla(id_regla, float(d["valor"]))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg})


@regla_bp.route("/<int:id_regla>", methods=["DELETE"])
def delete_regla(id_regla):
    exito, msg = eliminar_regla(id_regla)
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg})