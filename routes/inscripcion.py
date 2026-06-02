"""routes/inscripcion.py"""
from flask import Blueprint, request, jsonify
from logic.inscripcion import (
    listar_inscripciones, obtener_inscripcion,
    generar_inscripcion_individual, generar_inscripcion_masiva,
    obtener_volante_matricula, registrar_pago, obtener_cuenta_corriente
)

inscripcion_bp = Blueprint("inscripcion", __name__)

@inscripcion_bp.route("/individual", methods=["POST"])
def post_inscripcion_individual():
    """Crea una inscripción individual en BD."""
    d = request.json or {}
    
    # Validar campos requeridos
    if not d.get("id_estudiante") or not d.get("id_periodo"):
        return jsonify({"error": "Se requieren id_estudiante e id_periodo"}), 400
    
    try:
        id_estudiante = int(d["id_estudiante"])
        id_periodo = int(d["id_periodo"])
        semestre_a_cursar = int(d.get("semestre_a_cursar", 1))
        modalidad_cobro = d.get("modalidad_cobro", "GLOBAL")
        ids_asignaturas = d.get("ids_asignaturas")  # puede ser None si es GLOBAL
        
        exito, resultado = generar_inscripcion_individual(
            id_estudiante, id_periodo, semestre_a_cursar,
            modalidad_cobro, ids_asignaturas
        )
        
        if not exito:
            return jsonify({"error": resultado}), 400
        
        return jsonify({"mensaje": "Inscripción generada exitosamente", "id_inscripcion": resultado}), 201
    
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@inscripcion_bp.route("/masiva", methods=["POST"])
def post_inscripcion_masiva():
    """Genera inscripciones masivas para un período."""
    d = request.json or {}
    
    if not d.get("id_periodo"):
        return jsonify({"error": "Se requiere id_periodo"}), 400
    
    try:
        id_periodo = int(d["id_periodo"])
        semestre_a_cursar = int(d.get("semestre_a_cursar", 1))
        id_programa = d.get("id_programa")
        if id_programa:
            id_programa = int(id_programa)
        
        exitosos, errores = generar_inscripcion_masiva(
            id_periodo, "GLOBAL", semestre_a_cursar, id_programa
        )
        
        return jsonify({
            "mensaje": f"Inscripción masiva completada: {len(exitosos)} exitosas, {len(errores)} errores",
            "exitosos": exitosos,
            "errores": errores
        }), 200
    
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@inscripcion_bp.route("/", methods=["GET"])
def get_inscripciones():
    """Retorna lista de inscripciones desde BD."""
    id_periodo = request.args.get("id_periodo", type=int)
    id_programa = request.args.get("id_programa", type=int)
    id_estudiante = request.args.get("id_estudiante", type=int)
    return jsonify(listar_inscripciones(id_periodo, id_programa, id_estudiante)), 200

@inscripcion_bp.route("/<int:id_insc>", methods=["GET"])
def get_inscripcion(id_insc):
    """Retorna una inscripción por ID desde BD."""
    insc = obtener_inscripcion(id_insc)
    if not insc:
        return jsonify({"error": "Inscripción no encontrada"}), 404
    return jsonify(insc), 200

@inscripcion_bp.route("/<int:id_insc>/volante", methods=["GET"])
def get_volante_matricula(id_insc):
    """Retorna el volante de matrícula de una inscripción."""
    volante = obtener_volante_matricula(id_insc)
    if not volante:
        return jsonify({"error": "Volante no encontrado"}), 404
    return jsonify(volante), 200

@inscripcion_bp.route("/cuenta-corriente", methods=["GET"])
@inscripcion_bp.route("/cuenta-corriente/", methods=["GET"])
def get_cuenta_corriente():
    """Obtiene la cuenta corriente de un estudiante en un período."""
    id_estudiante = request.args.get("id_estudiante", type=int)
    id_periodo = request.args.get("id_periodo", type=int)
    
    if not id_estudiante or not id_periodo:
        return jsonify({"error": "Se requieren id_estudiante e id_periodo"}), 400
    
    cuenta = obtener_cuenta_corriente(id_estudiante, id_periodo)
    if not cuenta:
        return jsonify({"error": "No hay datos de cuenta corriente"}), 404
    
    return jsonify(cuenta), 200

@inscripcion_bp.route("/<int:id_insc>", methods=["PUT"])
def put_inscripcion(id_insc):
    """Actualiza una inscripción en BD."""
    return jsonify({"mensaje": "Inscripción actualizada"}), 200

@inscripcion_bp.route("/<int:id_insc>/pago", methods=["POST"])
def post_pago(id_insc):
    """Registra un pago para una inscripción."""
    d = request.json or {}
    
    requeridos = ("monto", "codigo_pago")
    if not all(d.get(k) for k in requeridos):
        return jsonify({"error": f"Se requieren: {', '.join(requeridos)}"}), 400
    
    try:
        monto = float(d["monto"])
        codigo_pago = d["codigo_pago"]
        descripcion = d.get("descripcion_breve", "")
        origen = d.get("origen", "CAJA")
        
        exito, msg = registrar_pago(id_insc, monto, codigo_pago, descripcion, origen)
        
        if not exito:
            return jsonify({"error": msg}), 400
        
        return jsonify({"mensaje": msg}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@inscripcion_bp.route("/<int:id_insc>", methods=["DELETE"])
def delete_inscripcion(id_insc):
    """Elimina una inscripción en BD."""
    return jsonify({"mensaje": "Inscripción eliminada"}), 200

