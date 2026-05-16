/**
 * ═════════════════════════════════════════════════════════════════════════════
 * UNIVERSIDAD CARIBE — SISTEMA DE GESTIÓN DE MATRÍCULAS
 * dashboard.js — Lógica del dashboard principal
 * ═════════════════════════════════════════════════════════════════════════════
 */

let ingresoChart = null;
let modalidadChart = null;

/**
 * Inicializa el dashboard
 */
async function initDashboard() {
  console.log('Inicializando dashboard...');
  
  try {
    // Cargar datos
    loadDashboardStats();
    loadCharts();
    
    console.log('✓ Dashboard inicializado correctamente');
  } catch (error) {
    console.error('Error al cargar el dashboard:', error);
  }
}

/**
 * Carga las estadísticas principales del dashboard
 */
async function loadDashboardStats() {
  try {
    // Llamar a la API para obtener datos reales
    const response = await fetch('/api/dashboard/stats');
    const stats = await response.json();

    // Actualizar elementos del DOM
    document.getElementById('totalEstudiantes').textContent = stats.total_estudiantes;
    document.getElementById('totalProgramas').textContent = stats.total_programas;
    document.getElementById('totalPeriodos').textContent = stats.total_periodos;
    document.getElementById('totalIngresos').textContent = fmtMoney(stats.ingresos_periodo);

    // Cargar estudiantes pendientes desde API
    const respPendientes = await fetch('/api/dashboard/estudiantes-pendientes');
    const estudiantesPendientes = await respPendientes.json();
    
    // Transformar datos para la tabla
    const estudiantesFormato = estudiantesPendientes.map(est => ({
      nombre: est.nombre,
      programa: est.programa,
      valor: Math.abs(est.saldo),
      dias: Math.floor(Math.random() * 30)
    }));
    
    loadEstudiantesPendientes(estudiantesFormato);

  } catch (error) {
    console.error('Error al cargar estadísticas:', error);
    // Fallback a datos mock si hay error
    const stats = {
      totalEstudiantes: 0,
      totalProgramas: 0,
      periodosActivos: 0,
      ingresosEsperados: 0
    };
    document.getElementById('totalEstudiantes').textContent = stats.totalEstudiantes;
    document.getElementById('totalProgramas').textContent = stats.totalProgramas;
    document.getElementById('totalPeriodos').textContent = stats.periodosActivos;
    document.getElementById('totalIngresos').textContent = fmtMoney(stats.ingresosEsperados);
  }
}

/**
 * Carga la lista de estudiantes pendientes de pago
 */
function loadEstudiantesPendientes(estudiantes) {
  const container = document.getElementById('estudiantesPendientes');
  
  if (!estudiantes || estudiantes.length === 0) {
    container.innerHTML = '<p class="text-muted text-center">Sin estudiantes pendientes</p>';
    return;
  }

  let html = '<div class="table-responsive"><table class="table table-sm mb-0"><tbody>';
  
  estudiantes.forEach(est => {
    const badge = est.dias > 15 ? 'danger' : (est.dias > 7 ? 'warning' : 'info');
    html += `
      <tr>
        <td>
          <strong>${est.nombre}</strong>
          <br><small class="text-muted">${est.programa}</small>
        </td>
        <td class="text-end">
          <div>${fmtMoney(est.valor)}</div>
          <small class="badge bg-${badge}">${est.dias} días</small>
        </td>
      </tr>
    `;
  });

  html += '</tbody></table></div>';
  container.innerHTML = html;
}

/**
 * Carga los gráficos del dashboard
 */
async function loadCharts() {
  try {
    // Gráfico de ingreso por programa
    const ctxIngreso = document.getElementById('ingresoChart');
    if (ctxIngreso) {
      if (ingresoChart) {
        ingresoChart.destroy();
      }
      
      try {
        // Obtener datos reales desde la API
        const respIngresos = await fetch('/api/dashboard/ingresos-por-programa');
        const ingresosPorPrograma = await respIngresos.json();
        
        const labels = ingresosPorPrograma.map(p => p.programa);
        const data = ingresosPorPrograma.map(p => p.ingresos);
        
        // Colores variados para cada barra
        const colores = ['#003366', '#006633', '#CC9900', '#FD7E14', '#DC3545', '#17a2b8', '#20c997', '#6f42c1'];
        const backgroundColor = labels.map((_, i) => colores[i % colores.length]);
        
        ingresoChart = new Chart(ctxIngreso, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Ingresos Esperados ($)',
              data: data,
              backgroundColor: backgroundColor,
              borderRadius: 6,
              borderSkipped: false
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: true,
                position: 'top'
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    if (value === 0) return '$0';
                    return '$' + (value / 1000000).toFixed(1) + 'M';
                  }
                }
              }
            }
          }
        });
      } catch (err) {
        console.error('Error al cargar ingresos por programa:', err);
      }
    }

    // Gráfico de modalidades de cobro
    const ctxModalidad = document.getElementById('modalidadChart');
    if (ctxModalidad) {
      if (modalidadChart) {
        modalidadChart.destroy();
      }
      
      try {
        // Obtener datos reales desde la API
        const respModalidades = await fetch('/api/dashboard/modalidades-cobro');
        const modalidades = await respModalidades.json();
        
        const labels = modalidades.map(m => m.modalidad_cobro);
        const data = modalidades.map(m => m.cantidad);
        
        modalidadChart = new Chart(ctxModalidad, {
          type: 'doughnut',
          data: {
            labels: labels.length > 0 ? labels : ['Sin datos'],
            datasets: [{
              data: data.length > 0 ? data : [1],
              backgroundColor: [
                '#003366',
                '#CC9900',
                '#006633',
                '#FD7E14'
              ],
              borderColor: '#fff',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: true,
                position: 'bottom'
              }
            }
          }
        });
      } catch (err) {
        console.error('Error al cargar modalidades de cobro:', err);
      }
    }

  } catch (error) {
    console.error('Error al cargar gráficos:', error);
  }
}

/**
 * Actualiza automáticamente las estadísticas cada 30 segundos
 */
function startAutoRefresh() {
  setInterval(() => {
    // loadDashboardStats(); // Descomentar cuando tengamos endpoints reales
  }, 30000);
}

/**
 * Inicialización al cargar la página
 */
document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
  startAutoRefresh();
});
