/**
 * Utilidades de accesibilidad
 */

/**
 * Genera un aria-label descriptivo para iconos
 */
export function getIconAriaLabel(iconClass, context = '') {
  const iconMap = {
    'fa-chart-bar': 'Gráfico',
    'fa-clipboard-list': 'Lista',
    'fa-palette': 'Paleta de colores',
    'fa-microchip': 'Tecnología',
    'fa-stream': 'Flujo',
    'fa-vial': 'Pruebas',
    'fa-users': 'Usuarios',
    'fa-eye': 'Ver',
    'fa-copy': 'Copiar',
    'fa-file-pdf': 'Exportar PDF',
    'fa-expand': 'Expandir',
    'fa-check-circle': 'Aprobado',
    'fa-exclamation-triangle': 'Advertencia',
    'fa-link': 'Dependencias',
    'fa-crown': 'Supervisor',
    'fa-sitemap': 'Coordinador',
    'fa-folder': 'Carpeta',
    'fa-bars': 'Menú',
    'fa-times': 'Cerrar',
    'fa-spinner': 'Cargando',
    'fa-birthday-cake': 'Edad',
    'fa-briefcase': 'Trabajo',
    'fa-bullseye': 'Objetivos',
    'fa-heart': 'Necesidades',
    'fa-route': 'Ruta',
    'fa-mobile-alt': 'Móvil',
    'fa-search-plus': 'Ampliar',
    'fa-external-link-alt': 'Enlace externo'
  };

  const iconKey = iconClass.replace('fas ', '').replace('fab ', '').replace('far ', '');
  const label = iconMap[iconKey] || 'Ícono';
  return context ? `${context} ${label}` : label;
}

/**
 * Maneja navegación por teclado para elementos interactivos
 */
export function handleKeyboardNavigation(event, onAction) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    onAction();
  }
}

