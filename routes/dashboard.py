"""routes/dashboard.py - Rutas para el dashboard"""
from flask import Blueprint, jsonify
from logic.dashboard import (obtener_estadisticas, obtener_estudiantes_pendientes,
                             obtener_ingresos_por_programa, obtener_modalidades_cobro)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/stats", methods=["GET"])
def get_stats():
    """Retorna estadísticas del dashboard desde BD."""
    stats = obtener_estadisticas()
    return jsonify(stats), 200

@dashboard_bp.route("/estudiantes-pendientes", methods=["GET"])
def get_estudiantes_pendientes():
    """Retorna estudiantes con pagos pendientes."""
    estudiantes = obtener_estudiantes_pendientes()
    return jsonify(estudiantes), 200

@dashboard_bp.route("/ingresos-por-programa", methods=["GET"])
def get_ingresos_por_programa():
    """Retorna ingresos esperados por programa desde BD."""
    ingresos = obtener_ingresos_por_programa()
    return jsonify(ingresos), 200

@dashboard_bp.route("/modalidades-cobro", methods=["GET"])
def get_modalidades_cobro():
    """Retorna distribución de modalidades de cobro desde BD."""
    modalidades = obtener_modalidades_cobro()
    return jsonify(modalidades), 200
