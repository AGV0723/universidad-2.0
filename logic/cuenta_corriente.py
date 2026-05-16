"""
Lógica de negocio para la cuenta corriente del estudiante.

La cuenta corriente concentra todos los movimientos (cobros y pagos) de un
estudiante en un periodo académico.  La regla de negocio central es:

    suma(COBROS) − suma(PAGOS) = saldo
    saldo == 0  →  cuenta balanceada

Este módulo se ocupa exclusivamente de *consultar* y *analizar* la cuenta.
Las operaciones de *escritura* (generar cobro, registrar pago) viven en
logic/inscripcion.py porque son parte del flujo de inscripción.

Funciones exportadas
────────────────────
obtener_cuenta_corriente(id_estudiante, id_periodo)
    → dict con movimientos, totales y saldo.

listar_cuentas_por_periodo(id_periodo, id_programa)
    → lista de resúmenes por estudiante (para reportes de gestión).

historial_cuentas_estudiante(id_estudiante)
    → todos los periodos con actividad del estudiante.

saldo_estudiante_periodo(id_estudiante, id_periodo)
    → float con el saldo actual (cobros − pagos).

estudiantes_pendientes_pago(id_periodo, id_programa)
    → lista de estudiantes con saldo > 0 en el periodo.

estudiantes_con_credito(id_periodo)
    → lista de estudiantes con saldo < 0 (pagaron de más / crédito financiero).
"""

from db import ejecutar_query


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def obtener_cuenta_corriente(id_estudiante: int, id_periodo: int) -> dict:
    """
    Devuelve todos los movimientos del estudiante en el periodo,
    ordenados cronológicamente, con totales y saldo calculados.

    Estructura de respuesta:
    {
        "movimientos": [ { monto, tipo, fecha, codigo, desc_codigo, ... } ],
        "total_cobros": float,
        "total_pagos":  float,
        "saldo":        float,   # cobros − pagos; 0 = balanceado
        "balanceado":   bool
    }
    """
    movimientos = ejecutar_query(
        """SELECT cc.id_movimiento,
                  cc.monto,
                  cc.tipo,
                  cc.fecha_movimiento,
                  cc.descripcion_breve,
                  cc.origen,
                  cd.codigo        AS codigo_detalle,
                  cd.descripcion   AS desc_codigo,
                  cd.grupo,
                  cc.id_inscripcion
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_estudiante = %s
             AND cc.id_periodo    = %s
           ORDER BY cc.fecha_movimiento ASC""",
        (id_estudiante, id_periodo)
    )

    total_cobros = sum(float(m["monto"]) for m in movimientos if m["tipo"] == "COBRO")
    total_pagos  = sum(float(m["monto"]) for m in movimientos if m["tipo"] == "PAGO")
    saldo        = round(total_cobros - total_pagos, 2)

    return {
        "movimientos":   movimientos,
        "total_cobros":  total_cobros,
        "total_pagos":   total_pagos,
        "saldo":         saldo,
        "balanceado":    abs(saldo) < 0.01,   # tolerancia de centavos
    }


# ─────────────────────────────────────────────────────────────────────────────
# RESÚMENES Y LISTADOS
# ─────────────────────────────────────────────────────────────────────────────

def listar_cuentas_por_periodo(id_periodo: int, id_programa: int = None) -> list:
    """
    Retorna un resumen de cuenta corriente por estudiante para un periodo.
    Útil para el reporte de ingreso esperado y el listado general de estudiantes.

    Parámetros opcionales:
        id_programa  → filtra por programa académico.
    """
    filtro_programa = "AND e.id_programa = %s" if id_programa else ""
    params = (id_periodo, id_programa) if id_programa else (id_periodo,)

    return ejecutar_query(
        f"""SELECT e.id_estudiante,
                   e.codigo_estudiantil,
                   CONCAT(e.primer_nombre, ' ', e.apellido) AS nombre_estudiante,
                   pr.nombre    AS nombre_programa,
                   i.modalidad_cobro,
                   i.semestre_a_cursar,
                   COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0) AS total_cobros,
                   COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO'  THEN cc.monto ELSE 0 END), 0) AS total_pagos,
                   COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0)
                   - COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0)
                                                                                            AS saldo
            FROM inscripcion i
            JOIN estudiante e          ON i.id_estudiante = e.id_estudiante
            JOIN programa_academico pr ON i.id_programa   = pr.id_programa
            LEFT JOIN cuenta_corriente cc
                   ON cc.id_estudiante = i.id_estudiante
                  AND cc.id_periodo    = i.id_periodo
            WHERE i.id_periodo = %s
              {filtro_programa}
            GROUP BY e.id_estudiante, e.codigo_estudiantil, nombre_estudiante,
                     pr.nombre, i.modalidad_cobro, i.semestre_a_cursar
            ORDER BY e.apellido, e.primer_nombre""",
        params
    )


def historial_cuentas_estudiante(id_estudiante: int) -> list:
    """
    Retorna todos los periodos académicos en los que el estudiante
    tiene movimientos en cuenta corriente, con el saldo de cada uno.
    """
    return ejecutar_query(
        """SELECT pa.id_periodo,
                  pa.codigo        AS codigo_periodo,
                  pa.descripcion   AS desc_periodo,
                  pa.fecha_inicio,
                  pa.fecha_fin,
                  COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0) AS total_cobros,
                  COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO'  THEN cc.monto ELSE 0 END), 0) AS total_pagos,
                  COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0) AS saldo
           FROM cuenta_corriente cc
           JOIN periodo_academico pa ON cc.id_periodo = pa.id_periodo
           WHERE cc.id_estudiante = %s
           GROUP BY pa.id_periodo, pa.codigo, pa.descripcion, pa.fecha_inicio, pa.fecha_fin
           ORDER BY pa.fecha_inicio DESC""",
        (id_estudiante,)
    )


def saldo_estudiante_periodo(id_estudiante: int, id_periodo: int) -> float:
    """
    Retorna únicamente el saldo numérico (cobros − pagos) del estudiante
    en el periodo indicado.  0.0 si no hay movimientos.
    """
    resultado = ejecutar_query(
        """SELECT COALESCE(SUM(CASE WHEN tipo = 'COBRO' THEN monto ELSE 0 END), 0)
                - COALESCE(SUM(CASE WHEN tipo = 'PAGO'  THEN monto ELSE 0 END), 0) AS saldo
           FROM cuenta_corriente
           WHERE id_estudiante = %s AND id_periodo = %s""",
        (id_estudiante, id_periodo), fetchone=True
    )
    return float(resultado["saldo"]) if resultado else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# REPORTES DE GESTIÓN
# ─────────────────────────────────────────────────────────────────────────────

def estudiantes_pendientes_pago(id_periodo: int, id_programa: int = None) -> list:
    """
    Lista los estudiantes con saldo > 0 (deben dinero) en el periodo.
    Reporte requerido: 'estudiantes pendientes de pago'.

    id_programa es obligatorio según el enunciado (el reporte lo solicita).
    Si se omite, retorna todos los programas.
    """
    filtro_programa = "AND e.id_programa = %s" if id_programa else ""
    params = (id_periodo, id_programa) if id_programa else (id_periodo,)

    return ejecutar_query(
        f"""SELECT e.id_estudiante,
                   e.codigo_estudiantil,
                   CONCAT(e.primer_nombre, ' ', e.apellido) AS nombre_estudiante,
                   e.correo,
                   pr.nombre    AS nombre_programa,
                   i.modalidad_cobro,
                   COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0)
                   - COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0)
                                                                                     AS saldo_pendiente
            FROM inscripcion i
            JOIN estudiante e          ON i.id_estudiante = e.id_estudiante
            JOIN programa_academico pr ON i.id_programa   = pr.id_programa
            LEFT JOIN cuenta_corriente cc
                   ON cc.id_estudiante = i.id_estudiante
                  AND cc.id_periodo    = i.id_periodo
            WHERE i.id_periodo = %s
              {filtro_programa}
            GROUP BY e.id_estudiante, e.codigo_estudiantil, nombre_estudiante,
                     e.correo, pr.nombre, i.modalidad_cobro
            HAVING saldo_pendiente > 0.01
            ORDER BY saldo_pendiente DESC""",
        params
    )


def estudiantes_con_credito(id_periodo: int) -> list:
    """
    Lista los estudiantes con saldo < 0 (crédito financiero / pagaron de más).
    Reporte requerido: 'cartera de crédito financiero'.
    Incluye el total de créditos para conocer el valor de cuentas por cobrar.
    """
    return ejecutar_query(
        """SELECT e.id_estudiante,
                  e.codigo_estudiantil,
                  CONCAT(e.primer_nombre, ' ', e.apellido) AS nombre_estudiante,
                  pr.nombre   AS nombre_programa,
                  ABS(
                    COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0)
                    - COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0)
                  )                                         AS valor_credito
           FROM inscripcion i
           JOIN estudiante e          ON i.id_estudiante = e.id_estudiante
           JOIN programa_academico pr ON i.id_programa   = pr.id_programa
           LEFT JOIN cuenta_corriente cc
                  ON cc.id_estudiante = i.id_estudiante
                 AND cc.id_periodo    = i.id_periodo
           WHERE i.id_periodo = %s
           GROUP BY e.id_estudiante, e.codigo_estudiantil, nombre_estudiante, pr.nombre
           HAVING (
               COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0)
               - COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0)
           ) < -0.01
           ORDER BY valor_credito DESC""",
        (id_periodo,)
    )


def ingreso_real_periodo(id_periodo: int) -> dict:
    """
    Retorna el total de pagos efectivamente recibidos en el periodo
    (ingreso real), desglosado por código de pago.
    Reporte requerido: 'ingreso real recibido en el periodo'.
    """
    detalle = ejecutar_query(
        """SELECT cd.codigo,
                  cd.descripcion,
                  SUM(cc.monto) AS total
           FROM cuenta_corriente cc
           JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
           WHERE cc.id_periodo = %s AND cc.tipo = 'PAGO'
           GROUP BY cd.codigo, cd.descripcion
           ORDER BY total DESC""",
        (id_periodo,)
    )
    total_general = sum(float(d["total"]) for d in detalle)
    return {"detalle": detalle, "total_general": total_general}