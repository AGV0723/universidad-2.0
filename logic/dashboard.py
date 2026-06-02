"""
logic/dashboard.py - Lógica para obtener estadísticas desde la BD
"""
from db import ejecutar_query

def obtener_estadisticas():
    """Retorna estadísticas reales desde la BD."""
    
    # Total de estudiantes
    total_est = ejecutar_query(
        "SELECT COUNT(*) as count FROM estudiante",
        fetchone=True
    )
    total_estudiantes = total_est['count'] if total_est else 0
    
    # Total de programas
    total_prog = ejecutar_query(
        "SELECT COUNT(*) as count FROM programa_academico",
        fetchone=True
    )
    total_programas = total_prog['count'] if total_prog else 0
    
    # Total de períodos
    total_per = ejecutar_query(
        "SELECT COUNT(*) as count FROM periodo_academico",
        fetchone=True
    )
    total_periodos = total_per['count'] if total_per else 0
    
    # Ingresos esperados (suma de todos los cobros registrados en cuenta_corriente)
    ingresos = ejecutar_query(
        """SELECT COALESCE(SUM(monto), 0) as total
           FROM cuenta_corriente
           WHERE tipo = 'COBRO'""",
        fetchone=True
    )
    ingresos_periodo = ingresos['total'] if ingresos else 0
    
    # Estudiantes por programa
    est_por_prog = ejecutar_query(
        """SELECT p.nombre, COUNT(e.id_estudiante) as cantidad
           FROM estudiante e
           JOIN programa_academico p ON e.id_programa = p.id_programa
           GROUP BY p.id_programa, p.nombre
           ORDER BY cantidad DESC
           LIMIT 10"""
    )
    
    labels_prog = [p['nombre'] for p in est_por_prog]
    data_prog = [p['cantidad'] for p in est_por_prog]
    
    return {
        "total_estudiantes": total_estudiantes,
        "total_programas": total_programas,
        "total_periodos": total_periodos,
        "ingresos_periodo": ingresos_periodo,
        "balance_cartera": 0,
        "estudiantes_activos": {
            "labels": labels_prog if labels_prog else ["Sin datos"],
            "data": data_prog if data_prog else [0]
        },
        "modalidades_pago": {
            "labels": ["Semestral", "Trimestral", "Mensual", "Crédito"],
            "data": [0, 0, 0, 0]
        }
    }

def obtener_ingresos_por_programa():
    """Retorna ingresos esperados por programa desde la BD."""
    return ejecutar_query(
        """SELECT 
              p.nombre as programa,
              COALESCE(SUM(cc.monto), 0) as ingresos
           FROM programa_academico p
           LEFT JOIN estudiante e ON p.id_programa = e.id_programa
           LEFT JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante AND cc.tipo = 'COBRO'
           GROUP BY p.id_programa, p.nombre
           ORDER BY ingresos DESC""",
        ()
    )

def obtener_modalidades_cobro():
    """Retorna distribución de modalidades de cobro desde la BD."""
    return ejecutar_query(
        """SELECT 
              modalidad_cobro,
              COUNT(*) as cantidad
           FROM inscripcion
           GROUP BY modalidad_cobro
           ORDER BY cantidad DESC""",
        ()
    )

def obtener_estudiantes_pendientes():
    """Retorna lista de estudiantes con pagos pendientes desde la BD."""
    return ejecutar_query(
        """SELECT 
              e.id_estudiante,
              CONCAT(e.primer_nombre, ' ', COALESCE(e.segundo_nombre, ''), ' ', e.apellido) as nombre,
              p.nombre as programa,
              (COALESCE(SUM(CASE WHEN cc.tipo = 'COBRO' THEN cc.monto ELSE 0 END), 0) - 
               COALESCE(SUM(CASE WHEN cc.tipo = 'PAGO' THEN cc.monto ELSE 0 END), 0)) as saldo,
              DATEDIFF(CURDATE(), MIN(CASE WHEN cc.tipo = 'COBRO' THEN cc.fecha_movimiento END)) as dias_pendiente,
              'PENDIENTE' as estado
            FROM estudiante e
            JOIN programa_academico p ON e.id_programa = p.id_programa
            LEFT JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante
            GROUP BY e.id_estudiante, e.primer_nombre, e.segundo_nombre, e.apellido, p.nombre
            HAVING saldo > 0
            ORDER BY saldo DESC
            LIMIT 10""",
        ()
    )

