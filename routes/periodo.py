"""routes/periodo.py - Rutas de Períodos Académicos"""
from flask import Blueprint, request, jsonify
from logic.periodo import listar_periodos, obtener_periodo, crear_periodo, actualizar_periodo

periodo_bp = Blueprint("periodo", __name__)

@periodo_bp.route("/", methods=["GET"])
def get_periodos():
    """Retorna lista de períodos desde BD."""
    solo_activos = request.args.get("activos", "false").lower() == "true"
    return jsonify(listar_periodos(solo_activos)), 200

@periodo_bp.route("/<int:id_periodo>", methods=["GET"])
def get_periodo(id_periodo):
    """Retorna un período por ID desde BD."""
    p = obtener_periodo(id_periodo)
    if not p:
        return jsonify({"error": "Período no encontrado"}), 404
    return jsonify(p), 200

@periodo_bp.route("/", methods=["POST"])
def post_periodo():
    """Crea un período en BD."""
    d = request.json or {}
    requeridos = ("codigo", "descripcion", "fecha_inicio", "fecha_fin")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Faltan campos: {', '.join(requeridos)}"}), 400
    exito, resultado = crear_periodo(d["codigo"], d["descripcion"],
                                     d["fecha_inicio"], d["fecha_fin"])
    if not exito:
        return jsonify({"error": resultado}), 409
    return jsonify({"mensaje": "Período creado", "id_periodo": resultado}), 201

@periodo_bp.route("/<int:id_periodo>", methods=["PUT"])
def put_periodo(id_periodo):
    """Actualiza un período en BD."""
    d = request.json or {}
    exito, msg = actualizar_periodo(id_periodo,
                                    descripcion=d.get("descripcion"),
                                    fecha_inicio=d.get("fecha_inicio"),
                                    fecha_fin=d.get("fecha_fin"),
                                    activo=d.get("activo"))
    if not exito:
        return jsonify({"error": msg}), 400
    return jsonify({"mensaje": msg}), 200


