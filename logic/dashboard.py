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
    
    # Ingresos esperados (suma de todas las inscripciones)
    ingresos = ejecutar_query(
        """SELECT COALESCE(SUM(rc.valor), 0) as total
           FROM inscripcion i
           JOIN regla_cobro rc ON i.id_programa = rc.id_programa
           WHERE i.id_periodo = rc.id_periodo""",
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
              COALESCE(SUM(rc.valor), 0) as ingresos
           FROM programa_academico p
           LEFT JOIN regla_cobro rc ON p.id_programa = rc.id_programa
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
             COALESCE(SUM(cc.monto), 0) as saldo,
             'PENDIENTE' as estado
           FROM estudiante e
           JOIN programa_academico p ON e.id_programa = p.id_programa
           LEFT JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante
           GROUP BY e.id_estudiante, e.primer_nombre, e.segundo_nombre, e.apellido, p.nombre
           HAVING saldo < 0
           LIMIT 10""",
        ()
    )

