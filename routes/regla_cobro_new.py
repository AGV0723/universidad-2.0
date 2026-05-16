"""routes/regla_cobro.py"""
from flask import Blueprint, request, jsonify
regla_bp = Blueprint("reglas", __name__)

@regla_bp.route("/", methods=["GET"])
def get_reglas():
    return jsonify([{"id": 1, "nombre": "Regla General", "tipo": "GLOBAL"}]), 200

@regla_bp.route("/", methods=["POST"])
def post_regla():
    return jsonify({"id": 99}), 201
