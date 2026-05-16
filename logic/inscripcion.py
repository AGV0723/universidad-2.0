"""
Núcleo del negocio: inscripción de estudiantes, generación de cobros
y gestión de la cuenta corriente.

Flujo completo:
  1. generar_inscripcion() → crea inscripcion + genera cobro en cuenta_corriente
  2. registrar_pago()      → registra pago en cuenta_corriente
  3. calcular_balance()    → COBROS - PAGOS = saldo del periodo
"""
from db import ejecutar_query, ejecutar_comando, ejecutar_transaccion
from logic.regla_cobro import obtener_regla_por_parametros
from logic.codigo_detalle import obtener_codigo_por_codigo
from logic.asignatura import listar_asignaturas_disponibles_para_semestre

# INSCRIPCIÓN 

def obtener_inscripcion(id_inscripcion):
    return ejecutar_query(
        """SELECT i.*,
                  CONCAT(e.primer_nombre,' ',e.apellido) AS nombre_estudiante,
                  e.codigo_estudiantil,
                  p.codigo AS codigo_periodo, p.descripcion AS desc_periodo,
                  pr.nombre AS nombre_programa
           FROM inscripcion i
           JOIN estudiante e ON i.id_estudiante = e.id_estudiante
           JOIN periodo_academico p ON i.id_periodo = p.id_periodo
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           WHERE i.id_inscripcion = %s""",
        (id_inscripcion,), fetchone=True
    )


def listar_inscripciones(id_periodo=None, id_programa=None):
    condiciones = []
    params = []
    if id_periodo:
        condiciones.append("i.id_periodo = %s"); params.append(id_periodo)
    if id_programa:
        condiciones.append("i.id_programa = %s"); params.append(id_programa)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    return ejecutar_query(
        f"""SELECT i.*,
                   CONCAT(e.primer_nombre,' ',e.apellido) AS nombre_estudiante,
                   e.codigo_estudiantil,
                   p.codigo AS codigo_periodo,
                   pr.nombre AS nombre_programa
            FROM inscripcion i
            JOIN estudiante e ON i.id_estudiante = e.id_estudiante
            JOIN periodo_academico p ON i.id_periodo = p.id_periodo
            JOIN programa_academico pr ON i.id_programa = pr.id_programa
            {where}
            ORDER BY e.apellido, e.primer_nombre""",
        tuple(params)
    )


def generar_inscripcion_individual(id_estudiante, id_periodo, semestre_a_cursar,
                                    modalidad_cobro, ids_asignaturas=None):
    """
    Crea la inscripción de un estudiante para un periodo.
    Si la modalidad es POR_CREDITOS, ids_asignaturas debe ser una lista de IDs.
    Si la modalidad es GLOBAL, no se requieren asignaturas.

    Genera automáticamente el cobro en cuenta_corriente.
    Crea la cuenta corriente si el estudiante no la tiene para este periodo.

    Devuelve (True, id_inscripcion) o (False, mensaje_error)
    """
    from logic.estudiante import obtener_estudiante
    from logic.periodo import obtener_periodo

    #  Validaciones previas 
    estudiante = obtener_estudiante(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado."

    if not estudiante["activo"]:
        return False, "El estudiante no está activo."

    periodo = obtener_periodo(id_periodo)
    if not periodo:
        return False, "Periodo académico no encontrado."

    # Verificar que no tenga inscripción en este periodo
    if ejecutar_query(
        "SELECT id_inscripcion FROM inscripcion WHERE id_estudiante=%s AND id_periodo=%s",
        (id_estudiante, id_periodo), fetchone=True
    ):
        return False, "El estudiante ya tiene una inscripción en este periodo."

    modalidades_validas = ("GLOBAL", "POR_CREDITOS")
    if modalidad_cobro not in modalidades_validas:
        return False, f"Modalidad inválida. Debe ser: {', '.join(modalidades_validas)}"

    #  Obtener regla de cobro 
    regla = obtener_regla_por_parametros(id_periodo, estudiante["id_programa"], modalidad_cobro)
    if not regla:
        return False, (f"No existe regla de cobro '{modalidad_cobro}' para el programa "
                       f"'{estudiante['nombre_programa']}' en este periodo.")

    #  Calcular monto 
    operaciones = []

    if modalidad_cobro == "GLOBAL":
        monto_cobro = float(regla["valor"])
        codigo_det  = obtener_codigo_por_codigo("PMAT")
        if not codigo_det:
            return False, "Código de detalle PMAT no encontrado. Verifique los códigos de detalle."

    else:  # POR_CREDITOS
        if not ids_asignaturas:
            return False, "Para modalidad POR_CREDITOS debe seleccionar al menos una asignatura."

        # Validar que todas las asignaturas estén disponibles para este estudiante
        disponibles = listar_asignaturas_disponibles_para_semestre(
            estudiante["id_pensum"], semestre_a_cursar, id_estudiante
        )
        ids_disponibles = {a["id_asignatura"] for a in disponibles}

        total_creditos = 0
        asignaturas_a_inscribir = []

        for id_asig in ids_asignaturas:
            if id_asig not in ids_disponibles:
                return False, (f"La asignatura {id_asig} no está disponible "
                               f"(prerequisito pendiente o fuera del rango de semestres).")
            asig = next(a for a in disponibles if a["id_asignatura"] == id_asig)
            total_creditos += asig["creditos"]
            asignaturas_a_inscribir.append(asig)

        monto_cobro = float(regla["valor"]) * total_creditos
        codigo_det  = obtener_codigo_por_codigo("PCRE")
        if not codigo_det:
            return False, "Código de detalle PCRE no encontrado. Verifique los códigos de detalle."

    #  Ejecutar en transacción 
    try:
        # 1. Insertar inscripción
        sql_inscripcion = """
            INSERT INTO inscripcion
              (modalidad_cobro, semestre_a_cursar, id_estudiante, id_programa, id_pensum, id_periodo)
            VALUES (%s,%s,%s,%s,%s,%s)
        """
        params_inscripcion = (
            modalidad_cobro, semestre_a_cursar,
            id_estudiante, estudiante["id_programa"],
            estudiante["id_pensum"], id_periodo
        )

        # Ejecutar inscripción primero para obtener su ID
        id_inscripcion = ejecutar_comando(sql_inscripcion, params_inscripcion)

        # 2. Si es POR_CREDITOS, registrar las asignaturas
        if modalidad_cobro == "POR_CREDITOS":
            for asig in asignaturas_a_inscribir:
                ejecutar_comando(
                    """INSERT INTO inscripcion_asignatura
                       (id_inscripcion, id_asignatura, semestre_snapshot, creditos_snapshot, prerequisitos_validados)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (id_inscripcion, asig["id_asignatura"],
                     asig["semestre"], asig["creditos"], True)
                )
                # Registrar en historial como EN_CURSO
                ejecutar_comando(
                    """INSERT INTO historial_academico
                       (id_estudiante, id_asignatura, id_periodo, estado)
                       VALUES (%s,%s,%s,'EN_CURSO')""",
                    (id_estudiante, asig["id_asignatura"], id_periodo)
                )

        # 3. Generar cobro en cuenta corriente
        ejecutar_comando(
            """INSERT INTO cuenta_corriente
               (monto, tipo, descripcion_breve, origen, id_estudiante, id_periodo, id_codigo_detalle, id_inscripcion)
               VALUES (%s,'COBRO',%s,'INDIVIDUAL',%s,%s,%s,%s)""",
            (monto_cobro,
             f"Matrícula {modalidad_cobro} - Semestre {semestre_a_cursar}",
             id_estudiante, id_periodo, codigo_det["id_codigo"], id_inscripcion)
        )

        return True, id_inscripcion

    except Exception as e:
        return False, f"Error al generar inscripción: {str(e)}"

def generar_inscripcion_masiva(id_periodo, modalidad_cobro, semestre_a_cursar,
                                id_programa=None):
    """
    Genera inscripciones para todos los estudiantes activos de un programa
    (o de todos los programas) que no tengan inscripción en el periodo.
    Solo funciona con modalidad GLOBAL.
    Devuelve (exitosos, errores) como listas.
    """
    if modalidad_cobro != "GLOBAL":
        return [], [{"error": "La generación masiva solo aplica para modalidad GLOBAL."}]

    from logic.estudiante import listar_estudiantes
    estudiantes = listar_estudiantes(solo_activos=True, id_programa=id_programa)

    exitosos = []
    errores  = []

    for est in estudiantes:
        # Saltar si ya tiene inscripción
        ya_inscrito = ejecutar_query(
            "SELECT id_inscripcion FROM inscripcion WHERE id_estudiante=%s AND id_periodo=%s",
            (est["id_estudiante"], id_periodo), fetchone=True
        )
        if ya_inscrito:
            continue

        exito, resultado = generar_inscripcion_individual(
            est["id_estudiante"], id_periodo, semestre_a_cursar, modalidad_cobro
        )

        if exito:
            exitosos.append({"estudiante": est["nombre_completo"], "id_inscripcion": resultado})
        else:
            errores.append({"estudiante": est["nombre_completo"], "error": resultado})

    return exitosos, errores

#  CUENTA CORRIENTE 

def registrar_pago(id_inscripcion, monto, codigo_pago, descripcion_breve, origen="CAJA"):
    """
    Registra un pago en la cuenta corriente del estudiante.
    origen: CAJA | EN_LINEA
    codigo_pago: código alfanumérico (ej: 'MPAG', 'ANT', 'DESC', 'CRED')
    """
    inscripcion = obtener_inscripcion(id_inscripcion)
    if not inscripcion:
        return False, "Inscripción no encontrada."

    origenes_validos = ("CAJA", "EN_LINEA")
    if origen not in origenes_validos:
        return False, f"Origen inválido. Debe ser: {', '.join(origenes_validos)}"

    if monto <= 0:
        return False, "El monto debe ser mayor que cero."

    codigo_det = obtener_codigo_por_codigo(codigo_pago)
    if not codigo_det:
        return False, f"Código de pago '{codigo_pago}' no encontrado."

    if codigo_det["grupo"] != "PAGO":
        return False, f"El código '{codigo_pago}' es de grupo {codigo_det['grupo']}, no PAGO."

    ejecutar_comando(
        """INSERT INTO cuenta_corriente
           (monto, tipo, descripcion_breve, origen, id_estudiante, id_periodo, id_codigo_detalle, id_inscripcion)
           VALUES (%s,'PAGO',%s,%s,%s,%s,%s,%s)""",
        (monto, descripcion_breve, origen,
         inscripcion["id_estudiante"], inscripcion["id_periodo"],
         codigo_det["id_codigo"], id_inscripcion)
    )
    return True, "Pago registrado exitosamente."

def obtener_cuenta_corriente(id_estudiante, id_periodo):
    """
    Devuelve todos los movimientos del estudiante en el periodo,
    con el saldo calculado al final.
    Regla: suma(COBROS) - suma(PAGOS) = 0 cuando está balanceado.
    """
    movimientos = ejecutar_query(
        """SELECT cc.*, cd.codigo, cd.descripcion AS desc_codigo, cd.grupo
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_estudiante=%s AND cc.id_periodo=%s
           ORDER BY cc.fecha_movimiento""",
        (id_estudiante, id_periodo)
    )

    # Calcular saldo: cobros - pagos
    total_cobros = sum(float(m["monto"]) for m in movimientos if m["tipo"] == "COBRO")
    total_pagos  = sum(float(m["monto"]) for m in movimientos if m["tipo"] == "PAGO")
    saldo        = total_cobros - total_pagos

    return {
        "movimientos": movimientos,
        "total_cobros": total_cobros,
        "total_pagos": total_pagos,
        "saldo": saldo,
        "balanceado": abs(saldo) < 0.01  # tolerancia de centavos
    }

def obtener_volante_matricula(id_inscripcion):
    """
    Genera el volante de matrícula: resumen de cobros del periodo.
    Muestra el detalle de lo que debe pagar el estudiante.
    """
    inscripcion = obtener_inscripcion(id_inscripcion)
    if not inscripcion:
        return None

    cobros = ejecutar_query(
        """SELECT cc.monto, cc.descripcion_breve, cd.codigo, cd.descripcion AS desc_codigo
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_inscripcion=%s AND cc.tipo='COBRO'""",
        (id_inscripcion,)
    )

    # Si es POR_CREDITOS, incluir el detalle de asignaturas
    asignaturas = []
    if inscripcion["modalidad_cobro"] == "POR_CREDITOS":
        asignaturas = ejecutar_query(
            """SELECT a.codigo, a.nombre, ia.creditos_snapshot, ia.semestre_snapshot
               FROM inscripcion_asignatura ia
               JOIN asignatura a ON ia.id_asignatura = a.id_asignatura
               WHERE ia.id_inscripcion=%s""",
            (id_inscripcion,)
        )

    total = sum(float(c["monto"]) for c in cobros)

    return {
        "inscripcion": inscripcion,
        "cobros": cobros,
        "asignaturas": asignaturas,
        "total": total
    }
