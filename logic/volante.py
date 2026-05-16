"""
Lógica para la gestión de volantes de matrícula.

Un volante de matrícula es el resumen detallado de los cobros que debe realizar
un estudiante en un período académico. Agrupa todos los cargos por concepto.

Funciones exportadas:
    obtener_volante(id_inscripcion)
        → dict con detalles de la matrícula, cobros y total
    
    listar_volantes(id_periodo, id_programa, id_estudiante)
        → lista de resúmenes de volantes para un filtro
    
    obtener_volante_estudiante_periodo(id_estudiante, id_periodo)
        → volante del estudiante para el periodo (si existe inscripción)
"""

from db import ejecutar_query


def obtener_volante(id_inscripcion: int) -> dict:
    """
    Genera el volante de matrícula: resumen de cobros del período.
    Muestra el detalle completo de lo que debe pagar el estudiante.

    Estructura de respuesta:
    {
        "inscripcion": { ... datos de inscripción },
        "cobros": [ { monto, descripcion_breve, codigo, desc_codigo } ],
        "asignaturas": [ { codigo, nombre, creditos, semestre } ],  # si es POR_CREDITOS
        "total": float,
        "total_pagado": float,
        "saldo_pendiente": float
    }
    """
    inscripcion = ejecutar_query(
        """SELECT i.*,
                  CONCAT(e.primer_nombre,' ',e.apellido) AS nombre_estudiante,
                  e.codigo_estudiantil,
                  e.correo,
                  e.telefono,
                  p.codigo AS codigo_periodo,
                  p.descripcion AS desc_periodo,
                  p.fecha_inicio,
                  p.fecha_fin,
                  pr.nombre AS nombre_programa
           FROM inscripcion i
           JOIN estudiante e ON i.id_estudiante = e.id_estudiante
           JOIN periodo_academico p ON i.id_periodo = p.id_periodo
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           WHERE i.id_inscripcion = %s""",
        (id_inscripcion,), fetchone=True
    )

    if not inscripcion:
        return None

    cobros = ejecutar_query(
        """SELECT cc.monto,
                  cc.descripcion_breve,
                  cd.codigo,
                  cd.descripcion AS desc_codigo,
                  cc.fecha_movimiento
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_inscripcion=%s AND cc.tipo='COBRO'
           ORDER BY cc.fecha_movimiento ASC""",
        (id_inscripcion,)
    )

    pagos = ejecutar_query(
        """SELECT cc.monto,
                  cc.descripcion_breve,
                  cd.codigo,
                  cd.descripcion AS desc_codigo,
                  cc.fecha_movimiento
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_inscripcion=%s AND cc.tipo='PAGO'
           ORDER BY cc.fecha_movimiento ASC""",
        (id_inscripcion,)
    )

    asignaturas = []
    if inscripcion["modalidad_cobro"] == "POR_CREDITOS":
        asignaturas = ejecutar_query(
            """SELECT a.codigo,
                      a.nombre,
                      ia.creditos_snapshot AS creditos,
                      ia.semestre_snapshot AS semestre
               FROM inscripcion_asignatura ia
               JOIN asignatura a ON ia.id_asignatura = a.id_asignatura
               WHERE ia.id_inscripcion=%s
               ORDER BY ia.semestre_snapshot, a.codigo""",
            (id_inscripcion,)
        )

    total_cobros = sum(float(c["monto"]) for c in cobros)
    total_pagos = sum(float(p["monto"]) for p in pagos)
    saldo_pendiente = total_cobros - total_pagos

    return {
        "inscripcion": inscripcion,
        "cobros": cobros,
        "pagos": pagos,
        "asignaturas": asignaturas,
        "total_cobros": total_cobros,
        "total_pagado": total_pagos,
        "saldo_pendiente": saldo_pendiente,
    }


def listar_volantes(id_periodo: int, id_programa: int = None,
                    id_estudiante: int = None) -> list:
    """Lista todos los volantes de un período con resúmenes."""
    condiciones = ["i.id_periodo = %s"]
    params = [id_periodo]

    if id_programa:
        condiciones.append("i.id_programa = %s")
        params.append(id_programa)

    if id_estudiante:
        condiciones.append("i.id_estudiante = %s")
        params.append(id_estudiante)

    where = " AND ".join(condiciones)

    return ejecutar_query(
        f"""SELECT i.id_inscripcion,
                   i.id_estudiante,
                   i.id_periodo,
                   CONCAT(e.primer_nombre,' ',e.apellido) AS nombre_estudiante,
                   e.codigo_estudiantil,
                   pr.nombre AS nombre_programa,
                   i.modalidad_cobro,
                   i.semestre_a_cursar,
                   COALESCE(SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END), 0) AS total_cobros,
                   COALESCE(SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END), 0) AS total_pagado,
                   COALESCE(SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END), 0)
                   - COALESCE(SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END), 0) AS saldo_pendiente,
                   i.fecha_creacion
            FROM inscripcion i
            JOIN estudiante e ON i.id_estudiante = e.id_estudiante
            JOIN programa_academico pr ON i.id_programa = pr.id_programa
            LEFT JOIN cuenta_corriente cc ON cc.id_inscripcion = i.id_inscripcion
            WHERE {where}
            GROUP BY i.id_inscripcion, i.id_estudiante, i.id_periodo,
                     nombre_estudiante, e.codigo_estudiantil, pr.nombre,
                     i.modalidad_cobro, i.semestre_a_cursar, i.fecha_creacion
            ORDER BY e.apellido, e.primer_nombre""",
        tuple(params)
    )


def obtener_volante_estudiante_periodo(id_estudiante: int, id_periodo: int) -> dict:
    """Obtiene el volante del estudiante para un período específico."""
    inscripcion = ejecutar_query(
        """SELECT id_inscripcion FROM inscripcion
           WHERE id_estudiante=%s AND id_periodo=%s LIMIT 1""",
        (id_estudiante, id_periodo), fetchone=True
    )

    if not inscripcion:
        return None

    return obtener_volante(inscripcion["id_inscripcion"])


def contar_volantes_periodo(id_periodo: int) -> int:
    """Retorna el total de volantes generados en un período."""
    resultado = ejecutar_query(
        "SELECT COUNT(*) AS total FROM inscripcion WHERE id_periodo = %s",
        (id_periodo,), fetchone=True
    )
    return resultado["total"] if resultado else 0
