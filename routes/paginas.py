"""routes/paginas.py - Rutas para servir páginas HTML"""
from flask import Blueprint, render_template, session, redirect
from functools import wraps

paginas_bp = Blueprint("paginas", __name__)

def requiere_no_estudiante(f):
    """Decorador que bloquea acceso a ESTUDIANTES a ciertas páginas."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_rol') == 'ESTUDIANTE':
            return redirect('/paginas/portal-pagos')
        return f(*args, **kwargs)
    return decorated_function

@paginas_bp.route("/estudiantes")
@requiere_no_estudiante
def estudiantes():
    return render_template("estudiantes.html")

@paginas_bp.route("/programas")
@requiere_no_estudiante
def programas():
    return render_template("programas.html")

@paginas_bp.route("/asignaturas")
@requiere_no_estudiante
def asignaturas():
    return render_template("asignaturas.html")

@paginas_bp.route("/periodos")
@requiere_no_estudiante
def periodos():
    return render_template("periodos.html")

@paginas_bp.route("/reglas")
@requiere_no_estudiante
def reglas():
    return render_template("reglas.html")

@paginas_bp.route("/codigos")
@requiere_no_estudiante
def codigos():
    return render_template("codigos.html")

@paginas_bp.route("/inscripciones")
@requiere_no_estudiante
def inscripciones():
    return render_template("inscripciones.html")

@paginas_bp.route("/reportes")
@requiere_no_estudiante
def reportes_page():
    return render_template("reportes.html")

@paginas_bp.route("/usuarios")
@requiere_no_estudiante
def usuarios():
    return render_template("usuarios.html")

@paginas_bp.route("/roles")
@requiere_no_estudiante
def roles():
    return render_template("roles.html")

@paginas_bp.route("/portal-pagos")
def portal_pagos():
    return render_template("portal-pagos.html")

@paginas_bp.route("/auditoria")
@requiere_no_estudiante
def auditoria():
    return render_template("auditoria.html")
