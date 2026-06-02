/*
 * Funciones globales y utilidades de la aplicación
 */

/*
 * FUNCIONES DE COMUNICACIÓN CON EL SERVIDOR (API)
*/

/**
 * Realiza una solicitud HTTP a la API.
 * @param {string} method - Método HTTP (GET, POST, PUT, DELETE)
 * @param {string} url - URL del endpoint
 * @param {object} body - Datos a enviar (para POST/PUT)
 * @returns {Promise} Respuesta JSON del servidor
 */
async function api(method, url, body = null) {
  spinner(true);
  try {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (body) {
      opts.body = JSON.stringify(body);
    }
    const response = await fetch(url, opts);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || `Error ${response.status}`);
    }
    return data;
  } catch (error) {
    showToast(error.message, 'danger');
    throw error;
  } finally {
    spinner(false);
  }
}

/**
 * Realiza una solicitud GET.
 * @param {string} url - URL del endpoint
 * @returns {Promise} Respuesta del servidor
 */
async function apiGet(url) {
  return api('GET', url);
}

/**
 * Realiza una solicitud POST.
 * @param {string} url - URL del endpoint
 * @param {object} body - Datos a enviar
 * @returns {Promise} Respuesta del servidor
 */
async function apiPost(url, body) {
  return api('POST', url, body);
}

/**
 * Realiza una solicitud PUT.
 * @param {string} url - URL del endpoint
 * @param {object} body - Datos a enviar
 * @returns {Promise} Respuesta del servidor
 */
async function apiPut(url, body) {
  return api('PUT', url, body);
}

/**
 * Realiza una solicitud DELETE.
 * @param {string} url - URL del endpoint
 * @returns {Promise} Respuesta del servidor
 */
async function apiDelete(url) {
  return api('DELETE', url);
}

/*
 * NOTIFICACIONES (TOASTS)
 */

/**
 * Muestra una notificación flotante (toast).
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: 'success', 'danger', 'warning', 'info'
 * @param {number} duration - Duración en milisegundos (3500 por defecto)
 */
function showToast(message, type = 'success', duration = 3500) {
  const colors = {
    success: 'bg-success',
    danger: 'bg-danger',
    warning: 'bg-warning text-dark',
    info: 'bg-info text-dark'
  };

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white ${colors[type] || colors.success} border-0 show`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;

  document.getElementById('toastContainer').appendChild(toast);
  const bsToast = new bootstrap.Toast(toast, { delay: duration });
  bsToast.show();

  setTimeout(() => toast.remove(), duration + 500);
}

/*SPINNER DE CARGA*/

/**
 * Muestra u oculta el spinner global de carga.
 * @param {boolean} show - true para mostrar, false para ocultar
 */
function spinner(show) {
  const spinnerEl = document.getElementById('globalSpinner');
  if (spinnerEl) {
    spinnerEl.classList.toggle('show', show);
  }
}

/* FORMATEO DE DATOS */

/**
 * Formatea un número como moneda en pesos colombianos.
 * @param {number} value - Valor a formatear
 * @returns {string} Valor formateado (ej: $1.234.567)
 */
function fmtMoney(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0
  }).format(value || 0);
}

/**
 * Formatea una fecha en formato corto.
 * @param {string|Date} date - Fecha a formatear
 * @returns {string} Fecha formateada (ej: 15/05/2026)
 */
function fmtDate(date) {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('es-CO');
}

/**
 * Formatea una fecha y hora.
 * @param {string|Date} dateTime - Fecha y hora a formatear
 * @returns {string} Fecha y hora formateadas
 */
function fmtDateTime(dateTime) {
  if (!dateTime) return '-';
  const date = new Date(dateTime);
  return date.toLocaleDateString('es-CO') + ' ' + date.toLocaleTimeString('es-CO');
}

/**
 * Formatea un número con decimales.
 * @param {number} value - Valor a formatear
 * @param {number} decimals - Cantidad de decimales (2 por defecto)
 * @returns {string} Valor formateado
 */
function fmtNumber(value, decimals = 2) {
  return new Intl.NumberFormat('es-CO', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value || 0);
}

/*VALIDACIÓN DE FORMULARIOS*/

/**
 * Valida un email.
 * @param {string} email - Email a validar
 * @returns {boolean} true si es válido
 */
function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Valida un número de documento colombiano.
 * @param {string} doc - Documento a validar
 * @returns {boolean} true si parece válido
 */
function isValidDocument(doc) {
  return doc && doc.trim().length >= 5;
}

/**
 * Valida que un campo no esté vacío.
 * @param {string} value - Valor a validar
 * @returns {boolean} true si no está vacío
 */
function isNotEmpty(value) {
  return value && value.toString().trim().length > 0;
}

/*MANIPULACIÓN DEL DOM*/

/**
 * Obtiene el valor de un input o select.
 * @param {string} selector - Selector CSS del elemento
 * @returns {string} Valor del elemento
 */
function getFormValue(selector) {
  const el = document.querySelector(selector);
  return el ? el.value : '';
}

/**
 * Establece el valor de un input o select.
 * @param {string} selector - Selector CSS del elemento
 * @param {string} value - Valor a asignar
 */
function setFormValue(selector, value) {
  const el = document.querySelector(selector);
  if (el) {
    el.value = value;
  }
}

/**
 * Limpia un formulario completo.
 * @param {string} formSelector - Selector CSS del formulario
 */
function clearForm(formSelector) {
  const form = document.querySelector(formSelector);
  if (form) {
    form.reset();
  }
}

/**
 * Muestra u oculta un elemento.
 * @param {string} selector - Selector CSS del elemento
 * @param {boolean} show - true para mostrar, false para ocultar
 */
function toggleElement(selector, show) {
  const el = document.querySelector(selector);
  if (el) {
    el.classList.toggle('d-none', !show);
  }
}

/**
 * Inserta HTML en un elemento.
 * @param {string} selector - Selector CSS del elemento
 * @param {string} html - HTML a insertar
 */
function setHTML(selector, html) {
  const el = document.querySelector(selector);
  if (el) {
    el.innerHTML = html;
  }
}

/*UTILIDADES DE ARRAYS Y OBJETOS*/

/**
 * Busca un valor en un array de objetos.
 * @param {array} array - Array a buscar
 * @param {string} key - Propiedad a comparar
 * @param {any} value - Valor buscado
 * @returns {object|null} Objeto encontrado o null
 */
function findInArray(array, key, value) {
  return array.find(item => item[key] === value) || null;
}

/**
 * Agrupa un array por una propiedad.
 * @param {array} array - Array a agrupar
 * @param {string} key - Propiedad para agrupar
 * @returns {object} Objeto con grupos
 */
function groupBy(array, key) {
  return array.reduce((result, item) => {
    const groupKey = item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
}

/**
 * Suma valores de un array de objetos.
 * @param {array} array - Array a sumar
 * @param {string} key - Propiedad a sumar
 * @returns {number} Suma total
 */
function sumArray(array, key) {
  return array.reduce((sum, item) => sum + (parseFloat(item[key]) || 0), 0);
}

/*MANEJO DE SESIONES Y AUTENTICACIÓN*/

/**
 * Obtiene información de la sesión actual.
 * @returns {object} Datos de sesión (desde el servidor)
 */
async function getSessionInfo() {
  try {
    const data = await apiGet('/seguridad/sesion');
    return data;
  } catch {
    return null;
  }
}

/**
 * Verifica si el usuario tiene un rol específico.
 * @param {string} rol - Rol a verificar
 * @returns {boolean} true si tiene el rol
 */
function hasRole(rol) {
  const roleEl = document.querySelector('[data-user-role]');
  return roleEl && roleEl.getAttribute('data-user-role') === rol;
}

/*ALMACENAMIENTO LOCAL (LocalStorage)*/

/**
 * Guarda un valor en localStorage.
 * @param {string} key - Clave
 * @param {any} value - Valor a guardar
 */
function setLocalStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    console.warn('No se pudo guardar en localStorage:', key);
  }
}

/**
 * Obtiene un valor de localStorage.
 * @param {string} key - Clave
 * @returns {any} Valor guardado o null
 */
function getLocalStorage(key) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch {
    console.warn('No se pudo leer de localStorage:', key);
    return null;
  }
}

/**
 * Elimina un valor de localStorage.
 * @param {string} key - Clave
 */
function removeLocalStorage(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    console.warn('No se pudo eliminar de localStorage:', key);
  }
}

/*TABLAS Y LISTADOS*/

/**
 * Crea una fila de tabla HTML a partir de un objeto.
 * @param {object} data - Datos de la fila
 * @param {array} columns - Nombres de columnas a mostrar
 * @returns {string} HTML de la fila
 */
function createTableRow(data, columns) {
  let html = '<tr>';
  columns.forEach(col => {
    const value = data[col] || '-';
    html += `<td>${value}</td>`;
  });
  html += '</tr>';
  return html;
}

/**
 * Crea una tabla HTML a partir de un array de objetos.
 * @param {array} data - Datos de la tabla
 * @param {array} columns - Columnas a mostrar
 * @param {array} headers - Encabezados (opcional)
 * @returns {string} HTML de la tabla
 */
function createTable(data, columns, headers = null) {
  let html = '<table class="table table-hover"><thead><tr>';

  const cols = headers || columns;
  cols.forEach(header => {
    html += `<th>${header}</th>`;
  });
  html += '</tr></thead><tbody>';

  data.forEach(row => {
    html += createTableRow(row, columns);
  });

  html += '</tbody></table>';
  return html;
}

/*FUNCIONES DE AUTENTICACIÓN*/

async function logout() {
  if (confirm('¿Está seguro de que desea cerrar sesión?')) {
    try {
      await api('POST', '/seguridad/logout');
    } catch (e) {
      console.warn('Error al cerrar sesión:', e);
    }
    window.location.href = '/seguridad/login';
  }
}

/*DIÁLOGOS Y CONFIRMACIONES*/

/**
 * Muestra un diálogo de confirmación.
 * @param {string} message - Mensaje de confirmación
 * @returns {Promise<boolean>} true si confirma, false si cancela
 */
function confirmAction(message) {
  return new Promise(resolve => {
    const modal = document.createElement('div');
    modal.className = 'modal d-block';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmación</h5>
          </div>
          <div class="modal-body">${message}</div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" id="btnCancel">Cancelar</button>
            <button type="button" class="btn btn-danger" id="btnConfirm">Confirmar</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('btnCancel').addEventListener('click', () => {
      document.body.removeChild(modal);
      resolve(false);
    });

    document.getElementById('btnConfirm').addEventListener('click', () => {
      document.body.removeChild(modal);
      resolve(true);
    });
  });
}

/**INICIALIZACIÓN*/

// Verifica que Bootstrap esté disponible
document.addEventListener('DOMContentLoaded', () => {
  // Inicialización de elementos Bootstrap con atributos
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Log para verificar que main.js se cargó
  console.log('✓ main.js cargado correctamente');
});

/*EXPORTAR PARA USO EN MÓDULOS*/

// En caso de que se use como módulo ES6
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    api, apiGet, apiPost, apiPut, apiDelete,
    showToast, spinner,
    fmtMoney, fmtDate, fmtDateTime, fmtNumber,
    isValidEmail, isValidDocument, isNotEmpty,
    getFormValue, setFormValue, clearForm, toggleElement, setHTML,
    findInArray, groupBy, sumArray,
    getSessionInfo, hasRole,
    setLocalStorage, getLocalStorage, removeLocalStorage,
    createTableRow, createTable,
    confirmAction
  };
}
