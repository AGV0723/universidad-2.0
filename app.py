"""
app.py — Punto de entrada de la aplicación Universidad Caribe.
Registra todos los blueprints y arranca el servidor Flask.
"""
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "universidad_caribe_dev")

# ── Importar blueprints ────────────────────────────────────────
from routes.programa         import programa_bp
from routes.asignatura       import asignatura_bp
from routes.estudiante       import estudiante_bp
from routes.periodo          import periodo_bp
from routes.regla_cobro      import regla_bp
from routes.codigo_detalle   import codigo_detalle_bp
from routes.inscripcion      import inscripcion_bp
from routes.volante          import volante_bp
from routes.cuenta_corriente import cuenta_corriente_bp
from routes.reportes         import reportes_bp
from routes.seguridad        import seguridad_bp
from routes.paginas          import paginas_bp
from routes.dashboard        import dashboard_bp
from routes.pensum           import pensum_bp

# ── Registrar blueprints con prefijos ─────────────────────────
app.register_blueprint(programa_bp,         url_prefix="/programas")
app.register_blueprint(asignatura_bp,       url_prefix="/asignaturas")
app.register_blueprint(estudiante_bp,       url_prefix="/estudiantes")
app.register_blueprint(periodo_bp,          url_prefix="/periodos")
app.register_blueprint(regla_bp,            url_prefix="/reglas")
app.register_blueprint(codigo_detalle_bp,   url_prefix="/codigos-detalle")
app.register_blueprint(inscripcion_bp,      url_prefix="/inscripciones")
app.register_blueprint(volante_bp,          url_prefix="/volantes")
app.register_blueprint(cuenta_corriente_bp, url_prefix="/cuentas-corriente")
app.register_blueprint(reportes_bp,         url_prefix="/reportes")
app.register_blueprint(seguridad_bp,        url_prefix="/seguridad")
app.register_blueprint(paginas_bp,          url_prefix="/paginas")
app.register_blueprint(dashboard_bp,        url_prefix="/api/dashboard")
app.register_blueprint(pensum_bp,           url_prefix="/pensum")


@app.route("/")
def index():
    from flask import session
    if not session.get('usuario_id'):
        from flask import redirect
        return redirect('/seguridad/login')
    return render_template("index.html")


# ── Manejo de errores ─────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
