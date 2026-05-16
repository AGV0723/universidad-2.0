"""routes/paginas.py - Rutas para servir páginas HTML"""
from flask import Blueprint, render_template

paginas_bp = Blueprint("paginas", __name__)

@paginas_bp.route("/estudiantes")
def estudiantes():
    return render_template("estudiantes.html")

@paginas_bp.route("/programas")
def programas():
    return render_template("programas.html")

@paginas_bp.route("/asignaturas")
def asignaturas():
    return render_template("asignaturas.html")

@paginas_bp.route("/periodos")
def periodos():
    return render_template("periodos.html")

@paginas_bp.route("/reglas")
def reglas():
    return render_template("reglas.html")

@paginas_bp.route("/codigos")
def codigos():
    return render_template("codigos.html")

@paginas_bp.route("/inscripciones")
def inscripciones():
    return render_template("inscripciones.html")

@paginas_bp.route("/reportes")
def reportes_page():
    return render_template("reportes.html")

@paginas_bp.route("/usuarios")
def usuarios():
    return render_template("usuarios.html")

@paginas_bp.route("/roles")
def roles():
    return render_template("roles.html")
