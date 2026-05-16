"""routes/reportes.py"""
from flask import Blueprint, request, jsonify
from logic.reportes import (reporte_estudiantes_con_cobro, reporte_ingreso_esperado_por_periodo,
                             reporte_pendientes_de_pago, reporte_ingreso_real,
                             reporte_credito_financiero)

reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.route("/estudiantes-cobro", methods=["GET"])
def get_reporte1():
    """Reporte 1: Estudiantes con programa, modalidad y monto."""
    id_periodo = request.args.get("id_periodo", type=int)
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    return jsonify(reporte_estudiantes_con_cobro(id_periodo)), 200

@reportes_bp.route("/ingreso-esperado", methods=["GET"])
def get_reporte2():
    """Reporte 2: Ingreso esperado por programa y periodo."""
    id_periodo = request.args.get("id_periodo", type=int)
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    return jsonify(reporte_ingreso_esperado_por_periodo(id_periodo)), 200

@reportes_bp.route("/pendientes-pago", methods=["GET"])
def get_reporte3():
    """Reporte 3: Estudiantes con pagos pendientes."""
    id_periodo = request.args.get("id_periodo", type=int)
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    return jsonify(reporte_pendientes_de_pago(id_periodo)), 200

@reportes_bp.route("/ingreso-real", methods=["GET"])
def get_reporte4():
    """Reporte 4: Ingreso real por período."""
    id_periodo = request.args.get("id_periodo", type=int)
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    return jsonify(reporte_ingreso_real(id_periodo)), 200

@reportes_bp.route("/credito-financiero", methods=["GET"])
def get_reporte5():
    """Reporte 5: Estudiantes con crédito financiero."""
    id_periodo = request.args.get("id_periodo", type=int)
    if not id_periodo:
        return jsonify({"error": "Se requiere id_periodo"}), 400
    return jsonify(reporte_credito_financiero(id_periodo)), 200

