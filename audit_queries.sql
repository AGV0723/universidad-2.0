-- ============================================================================
-- AUDITORÍA DE COBROS Y PAGOS - CUENTA CORRIENTE
-- ============================================================================

-- 1. RESUMEN GENERAL DE COBROS Y PAGOS
SELECT 
  tipo,
  COUNT(*) as cantidad,
  SUM(monto) as total
FROM cuenta_corriente
GROUP BY tipo;

-- 2. TOTALES ACUMULADOS
SELECT 
  SUM(CASE WHEN tipo='COBRO' THEN monto ELSE 0 END) as total_cobros,
  SUM(CASE WHEN tipo='PAGO' THEN monto ELSE 0 END) as total_pagos,
  SUM(CASE WHEN tipo='COBRO' THEN monto ELSE 0 END) - 
  SUM(CASE WHEN tipo='PAGO' THEN monto ELSE 0 END) as saldo_neto
FROM cuenta_corriente;

-- 3. SALDO POR ESTUDIANTE Y PERÍODO
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
ORDER BY cc.id_estudiante, cc.id_periodo;

-- 4. RESUMEN POR PERÍODO
SELECT 
  p.id_periodo,
  p.codigo as periodo,
  p.descripcion,
  COUNT(DISTINCT cc.id_estudiante) as estudiantes_con_movimientos,
  SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) as total_cobros,
  SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as total_pagos,
  SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
  SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END) as saldo_pendiente,
  COUNT(DISTINCT CASE WHEN cc.tipo='COBRO' THEN cc.id_estudiante END) as estudiantes_con_cobros,
  COUNT(DISTINCT CASE WHEN cc.tipo='PAGO' THEN cc.id_estudiante END) as estudiantes_con_pagos
FROM cuenta_corriente cc
RIGHT JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
GROUP BY p.id_periodo, p.codigo, p.descripcion
ORDER BY p.id_periodo;

-- 5. ÚLTIMOS 20 MOVIMIENTOS CON DETALLE
SELECT 
  cc.id_movimiento,
  DATE(cc.fecha_movimiento) as fecha,
  TIME(cc.fecha_movimiento) as hora,
  cc.tipo,
  cc.monto,
  e.codigo_estudiantil,
  CONCAT(e.primer_nombre, ' ', e.apellido) as estudiante,
  p.codigo as periodo,
  cd.codigo as codigo_detalle,
  cd.descripcion as desc_codigo,
  cc.descripcion_breve,
  cc.origen
FROM cuenta_corriente cc
JOIN estudiante e ON cc.id_estudiante = e.id_estudiante
JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
JOIN codigo_detalle cd ON cc.id_codigo_detalle = cd.id_codigo
ORDER BY cc.fecha_movimiento DESC, cc.id_movimiento DESC
LIMIT 20;

-- 6. ESTUDIANTES CON DEUDA PENDIENTE
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
GROUP BY e.id_estudiante, cc.id_periodo, e.codigo_estudiantil, e.primer_nombre, e.apellido, p.codigo
HAVING deuda_pendiente > 0.01
ORDER BY deuda_pendiente DESC, e.id_estudiante;

-- 7. ESTUDIANTES PAGADOS
SELECT 
  e.id_estudiante,
  e.codigo_estudiantil,
  CONCAT(e.primer_nombre, ' ', e.apellido) as estudiante,
  p.codigo as periodo,
  COUNT(DISTINCT cc.id_movimiento) as num_movimientos
FROM estudiante e
JOIN cuenta_corriente cc ON e.id_estudiante = cc.id_estudiante
JOIN periodo_academico p ON cc.id_periodo = p.id_periodo
GROUP BY e.id_estudiante, cc.id_periodo
HAVING ABS(
  SUM(CASE WHEN cc.tipo='COBRO' THEN cc.monto ELSE 0 END) - 
  SUM(CASE WHEN cc.tipo='PAGO' THEN cc.monto ELSE 0 END)
) < 0.01
ORDER BY e.id_estudiante;
