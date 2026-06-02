"""
routes/audit.py - Rutas para auditoria de pagos
"""
from flask import Blueprint, jsonify
from db import ejecutar_query

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/resumen-pagos", methods=["GET"])
def resumen_pagos():
    """Retorna resumen de cobros y pagos."""
    totales = ejecutar_query('''
    SELECT 
      tipo,
      COUNT(*) as cantidad,
      SUM(monto) as total
    FROM cuenta_corriente
    GROUP BY tipo
    ''')
    
    acumulado = ejecutar_query('''
    SELECT 
      SUM(CASE WHEN tipo='COBRO' THEN monto ELSE 0 END) as total_cobros,
      SUM(CASE WHEN tipo='PAGO' THEN monto ELSE 0 END) as total_pagos
    FROM cuenta_corriente
    ''')[0]
    
    return jsonify({
        "movimientos_por_tipo": totales,
        "acumulado": acumulado
    }), 200


@audit_bp.route("/saldos-estudiantes", methods=["GET"])
def saldos_estudiantes():
    """Retorna saldos por estudiante y período."""
    saldos = ejecutar_query('''
    SELECT 
      cc.id_estudiante,
      e.codigo_estudiantil,
      CONCAT(e.primer_nombre, ' ', COALESCE(e.segundo_nombre, ''), ' ', 
             e.apellido, ' ', COALESCE(e.segundo_apellido, '')) as estudiante,
      cc.id_periodo,
      p.codigo as periodo,
      SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) as cobros,
      SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as pagos,
      SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
      SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as saldo
    FROM cuenta_corriente cc
    JOIN estudiante e ON cc.id_estudiante = e.id_estudiante
    JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
    GROUP BY cc.id_estudiante, cc.id_periodo
    ORDER BY cc.id_estudiante, cc.id_periodo
    ''')
    
    return jsonify(saldos), 200


@audit_bp.route("/resumen-periodos", methods=["GET"])
def resumen_periodos():
    """Retorna resumen por período."""
    periodos = ejecutar_query('''
    SELECT 
      p.id_periodo,
      p.codigo as periodo,
      p.descripcion,
      COUNT(DISTINCT cc.id_estudiante) as estudiantes_con_movimientos,
      SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) as total_cobros,
      SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as total_pagos,
      SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
      SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as saldo_pendiente
    FROM cuenta_corriente cc
    RIGHT JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
    GROUP BY p.id_periodo, p.codigo, p.descripcion
    ORDER BY p.id_periodo
    ''')
    
    return jsonify(periodos), 200


@audit_bp.route("/ultimos-movimientos", methods=["GET"])
def ultimos_movimientos():
    """Retorna últimos 20 movimientos."""
    try:
        movimientos = ejecutar_query('''
        SELECT 
          cc.id_movimiento,
          cc.fecha_movimiento,
          cc.tipo,
          cc.monto,
          e.codigo_estudiantil,
          CONCAT(e.primer_nombre, ' ', e.apellido) as estudiante,
          p.codigo as periodo,
          cd.codigo as codigo_detalle,
          cc.descripcion_breve,
          cc.origen
        FROM cuenta_corriente cc
        JOIN estudiante e ON cc.id_estudiante = e.id_estudiante
        JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
        JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
        ORDER BY cc.fecha_movimiento DESC, cc.id_movimiento DESC
        LIMIT 20
        ''')
        
        # Formatear la fecha en el backend
        for mov in movimientos:
            if mov['fecha_movimiento']:
                fecha = mov['fecha_movimiento']
                mov['fecha'] = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)[:10]
                mov['hora'] = fecha.strftime('%H:%M:%S') if hasattr(fecha, 'strftime') else str(fecha)[11:19]
            else:
                mov['fecha'] = '-'
                mov['hora'] = '-'
            del mov['fecha_movimiento']
        
        return jsonify(movimientos), 200
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e), 
            "tipo": type(e).__name__,
            "traceback": traceback.format_exc()
        }), 500


@audit_bp.route("/estudiantes-deuda", methods=["GET"])
def estudiantes_deuda():
    """Retorna estudiantes con deuda pendiente."""
    deuda = ejecutar_query('''
    SELECT 
      e.id_estudiante,
      e.codigo_estudiantil,
      CONCAT(e.primer_nombre, ' ', e.apellido) as estudiante,
      p.codigo as periodo,
      ROUND(
        SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
        SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END), 2
      ) as deuda_pendiente,
      COUNT(DISTINCT cc.id_movimiento) as num_movimientos
    FROM estudiante e
    JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante
    JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
    GROUP BY e.id_estudiante, e.codigo_estudiantil, e.primer_nombre, e.apellido, cc.id_periodo, p.codigo
    HAVING deuda_pendiente > 0.01
    ORDER BY deuda_pendiente DESC, e.id_estudiante
    ''')
    
    return jsonify(deuda), 200


@audit_bp.route("/estudiantes-pagados", methods=["GET"])
def estudiantes_pagados():
    """Retorna estudiantes que han pagado todo."""
    pagados = ejecutar_query('''
    SELECT 
      e.id_estudiante,
      e.codigo_estudiantil,
      CONCAT(e.primer_nombre, ' ', e.apellido) as estudiante,
      p.codigo as periodo,
      COUNT(DISTINCT cc.id_movimiento) as num_movimientos
    FROM estudiante e
    JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante
    JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
    GROUP BY e.id_estudiante, e.codigo_estudiantil, e.primer_nombre, e.apellido, cc.id_periodo, p.codigo
    HAVING ABS(
      SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
      SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END)
    ) < 0.01
    ORDER BY e.id_estudiante
    ''')
    
    return jsonify(pagados), 200
