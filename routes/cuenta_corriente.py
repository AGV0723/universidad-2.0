"""routes/cuenta_corriente.py"""
from flask import Blueprint, request, jsonify
from logic.cuenta_corriente import (obtener_cuenta_corriente, listar_cuentas_por_periodo,
                                     historial_cuentas_estudiante, saldo_estudiante_periodo,
                                     estudiantes_pendientes_pago, estudiantes_con_credito,
                                     ingreso_real_periodo)

cuenta_corriente_bp = Blueprint("cuenta_corriente", __name__)

@cuenta_corriente_bp.route("/<int:id_estudiante>/<int:id_periodo>", methods=["GET"])
def get_cuenta_corriente(id_estudiante, id_periodo):
    """Obtiene la cuenta corriente de un estudiante en un período desde BD."""
    cuenta = obtener_cuenta_corriente(id_estudiante, id_periodo)
    if not cuenta or not cuenta.get("movimientos"):
        return jsonify({"error": "No hay movimientos en la cuenta corriente"}), 404
    return jsonify(cuenta), 200

@cuenta_corriente_bp.route("/<int:id_estudiante>/historial", methods=["GET"])
def get_historial(id_estudiante):
    """Retorna historial de cuentas de un estudiante."""
    return jsonify(historial_cuentas_estudiante(id_estudiante)), 200

@cuenta_corriente_bp.route("/<int:id_estudiante>/saldo/<int:id_periodo>", methods=["GET"])
def get_saldo(id_estudiante, id_periodo):
    """Retorna saldo de un estudiante en un período."""
    saldo = saldo_estudiante_periodo(id_estudiante, id_periodo)
    return jsonify({"id_estudiante": id_estudiante, "id_periodo": id_periodo, "saldo": saldo}), 200

@cuenta_corriente_bp.route("/pendientes/<int:id_periodo>", methods=["GET"])
def get_pendientes(id_periodo):
    """Retorna estudiantes con pagos pendientes en un período."""
    id_programa = request.args.get("id_programa", type=int)
    return jsonify(estudiantes_pendientes_pago(id_periodo, id_programa)), 200

@cuenta_corriente_bp.route("/credito/<int:id_periodo>", methods=["GET"])
def get_credito(id_periodo):
    """Retorna estudiantes con crédito financiero en un período."""
    return jsonify(estudiantes_con_credito(id_periodo)), 200

@cuenta_corriente_bp.route("/ingreso/<int:id_periodo>", methods=["GET"])
def get_ingreso(id_periodo):
    """Retorna ingreso real de un período."""
    ingreso = ingreso_real_periodo(id_periodo)
    return jsonify({"id_periodo": id_periodo, "ingreso_total": ingreso}), 200


    """Retorna el historial de todas las cuentas del estudiante."""
    historial = historial_cuentas_estudiante(id_estudiante)
    if not historial:
        return jsonify({"error": "El estudiante no tiene movimientos"}), 404
    return jsonify(historial)


@cuenta_corriente_bp.route("/<int:id_estudiante>/<int:id_periodo>/saldo", methods=["GET"])
def get_saldo_estudiante(id_estudiante, id_periodo):
    """Obtiene únicamente el saldo actual del estudiante en el período."""
    saldo = saldo_estudiante_periodo(id_estudiante, id_periodo)
    return jsonify({
        "id_estudiante": id_estudiante,
        "id_periodo": id_periodo,
        "saldo": saldo,
        "balanceado": abs(saldo) < 0.01
    })


@cuenta_corriente_bp.route("/periodo/<int:id_periodo>", methods=["GET"])
def get_cuentas_periodo(id_periodo):
    """Obtiene un resumen de todas las cuentas corrientes en un período."""
    id_programa = request.args.get("id_programa", type=int)
    cuentas = listar_cuentas_por_periodo(id_periodo, id_programa)
    if not cuentas:
        return jsonify({"error": "No hay cuentas en este período"}), 404
    return jsonify(cuentas)


# ── REPORTES ──────────────────────────────────────────────

@cuenta_corriente_bp.route("/reportes/pendientes-pago/<int:id_periodo>", methods=["GET"])
def reporte_pendientes_pago(id_periodo):
    """Reporte: Estudiantes pendientes de pago en el período."""
    id_programa = request.args.get("id_programa", type=int)
    if not id_programa:
        return jsonify({"error": "id_programa es requerido"}), 400

    pendientes = estudiantes_pendientes_pago(id_periodo, id_programa)
    if not pendientes:
        return jsonify({
            "mensaje": "No hay estudiantes pendientes de pago",
            "id_periodo": id_periodo,
            "id_programa": id_programa,
            "estudiantes": []
        })

    total_pendiente = sum(float(e["saldo_pendiente"]) for e in pendientes)
    return jsonify({
        "id_periodo": id_periodo,
        "id_programa": id_programa,
        "total_estudiantes": len(pendientes),
        "total_pendiente": total_pendiente,
        "estudiantes": pendientes
    })


@cuenta_corriente_bp.route("/reportes/credito-financiero/<int:id_periodo>", methods=["GET"])
def reporte_credito_financiero(id_periodo):
    """Reporte: Estudiantes con crédito financiero (cartera por cobrar)."""
    creditos = estudiantes_con_credito(id_periodo)
    if not creditos:
        return jsonify({
            "mensaje": "No hay estudiantes con crédito financiero",
            "id_periodo": id_periodo,
            "total_cartera": 0,
            "estudiantes": []
        })

    total_cartera = sum(float(e["valor_credito"]) for e in creditos)
    return jsonify({
        "id_periodo": id_periodo,
        "total_estudiantes": len(creditos),
        "total_cartera": total_cartera,
        "estudiantes": creditos
    })


@cuenta_corriente_bp.route("/reportes/ingreso-real/<int:id_periodo>", methods=["GET"])
def reporte_ingreso_real(id_periodo):
    """Reporte: Ingreso real recibido en el período desglosado por código."""
    ingreso = ingreso_real_periodo(id_periodo)
    return jsonify({
        "id_periodo": id_periodo,
        "detalle": ingreso["detalle"],
        "total_general": ingreso["total_general"]
    })


@cuenta_corriente_bp.route("/reportes/resumen/<int:id_periodo>", methods=["GET"])
def reporte_resumen_periodo(id_periodo):
    """Reporte: Resumen financiero completo del período."""
    cuentas = listar_cuentas_por_periodo(id_periodo)

    total_cobros = sum(float(c.get("total_cobros", 0)) for c in cuentas)
    total_pagos = sum(float(c.get("total_pagos", 0)) for c in cuentas)
    total_pendiente = sum(float(c.get("saldo", 0)) for c in cuentas if float(c.get("saldo", 0)) > 0)
    total_credito = sum(abs(float(c.get("saldo", 0))) for c in cuentas if float(c.get("saldo", 0)) < 0)

    return jsonify({
        "id_periodo": id_periodo,
        "total_estudiantes": len(cuentas),
        "total_cobros_esperado": total_cobros,
        "total_pagos_recibido": total_pagos,
        "total_saldo_pendiente": total_pendiente,
        "total_cartera_credito": total_credito,
        "balance_neto": total_cobros - total_pagos
    })
