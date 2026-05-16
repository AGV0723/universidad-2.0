"""
Los 5 reportes (queries) de gestión
Todos devuelven listas de diccionarios listos para mostrar.
"""
from db import ejecutar_query

def reporte_estudiantes_con_cobro(id_periodo):
    """
    Reporte 1: Listado de estudiantes con programa, modalidad de cobro y monto.
    """
    return ejecutar_query(
        """SELECT
               e.codigo_estudiantil,
               CONCAT(e.primer_nombre,' ',e.apellido) AS nombre,
               pr.nombre AS programa,
               i.modalidad_cobro,
               i.semestre_a_cursar,
               COALESCE(SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END), 0) AS monto_cobrado
           FROM inscripcion i
           JOIN estudiante e ON i.id_estudiante = e.id_estudiante
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           LEFT JOIN cuenta_corriente cc ON cc.id_inscripcion = i.id_inscripcion
           WHERE i.id_periodo = %s
           GROUP BY i.id_inscripcion
           ORDER BY pr.nombre, e.apellido""",
        (id_periodo,)
    )

def reporte_ingreso_esperado_por_periodo(id_periodo):
    """
    Reporte 2: Ingreso esperado totalizado por programa en el periodo.
    """
    return ejecutar_query(
        """SELECT
               pr.nombre AS programa,
               i.modalidad_cobro,
               COUNT(DISTINCT i.id_inscripcion) AS num_estudiantes,
               SUM(cc.monto) AS ingreso_esperado
           FROM inscripcion i
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           JOIN cuenta_corriente cc ON cc.id_inscripcion = i.id_inscripcion
                                    AND cc.tipo = 'COBRO'
           WHERE i.id_periodo = %s
           GROUP BY pr.id_programa, i.modalidad_cobro
           ORDER BY pr.nombre""",
        (id_periodo,)
    )

def reporte_pendientes_de_pago(id_periodo, id_programa):
    """
    Reporte 3: Estudiantes con saldo pendiente (cobros > pagos) en el periodo,
    filtrado por programa.
    """
    return ejecutar_query(
        """SELECT
               e.codigo_estudiantil,
               CONCAT(e.primer_nombre,' ',e.apellido) AS nombre,
               pr.nombre AS programa,
               i.modalidad_cobro,
               SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) AS total_cobrado,
               SUM(CASE WHEN cc.tipo='PAGO'  THEN cc.monto ELSE 0 END) AS total_pagado,
               SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) -
               SUM(CASE WHEN cc.tipo='PAGO'  THEN cc.monto ELSE 0 END) AS saldo_pendiente
           FROM inscripcion i
           JOIN estudiante e ON i.id_estudiante = e.id_estudiante
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           JOIN cuenta_corriente cc ON cc.id_inscripcion = i.id_inscripcion
           WHERE i.id_periodo = %s AND i.id_programa = %s
           GROUP BY i.id_inscripcion
           HAVING saldo_pendiente > 0.01
           ORDER BY saldo_pendiente DESC""",
        (id_periodo, id_programa)
    )

def reporte_ingreso_real(id_periodo):
    """
    Reporte 4: Ingreso real recibido (solo pagos) en el periodo.
    """
    return ejecutar_query(
        """SELECT
               pr.nombre AS programa,
               COUNT(DISTINCT i.id_inscripcion) AS num_estudiantes,
               SUM(cc.monto) AS ingreso_real
           FROM inscripcion i
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           JOIN cuenta_corriente cc ON cc.id_inscripcion = i.id_inscripcion
                                    AND cc.tipo = 'PAGO'
           WHERE i.id_periodo = %s
           GROUP BY pr.id_programa
           ORDER BY pr.nombre""",
        (id_periodo,)
    )

def reporte_credito_financiero(id_periodo):
    """
    Reporte 5: Estudiantes con crédito financiero (código CRED),
    con el valor del crédito y el total de cartera.
    """
    return ejecutar_query(
        """SELECT
               e.codigo_estudiantil,
               CONCAT(e.primer_nombre,' ',e.apellido) AS nombre,
               pr.nombre AS programa,
               SUM(cc.monto) AS valor_credito
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
                                  AND cd.codigo = 'CRED'
           JOIN inscripcion i ON cc.id_inscripcion = i.id_inscripcion
           JOIN estudiante e ON cc.id_estudiante = e.id_estudiante
           JOIN programa_academico pr ON i.id_programa = pr.id_programa
           WHERE cc.id_periodo = %s AND cc.tipo = 'PAGO'
           GROUP BY e.id_estudiante
           ORDER BY pr.nombre, e.apellido""",
        (id_periodo,)
    )
