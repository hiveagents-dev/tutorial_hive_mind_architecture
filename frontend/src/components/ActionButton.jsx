import React from 'react';

export function ActionButton({ 
  type = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon,
  children,
  onClick,
  className = '',
  ...props 
}) {
  const getButtonClass = () => {
    const baseClass = 'btn';
    const typeClass = `btn-${type}`;
    const sizeClass = `btn-${size}`;
    const loadingClass = loading ? 'loading' : '';
    const disabledClass = disabled ? 'disabled' : '';
    
    return `${baseClass} ${typeClass} ${sizeClass} ${loadingClass} ${disabledClass} ${className}`.trim();
  };

  // Generar aria-label si hay icono pero no texto descriptivo
  const ariaLabel = props['aria-label'] || (icon && !children ? 'Acción' : undefined);

  return (
    <button
      className={getButtonClass()}
      onClick={onClick}
      disabled={disabled || loading}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && !disabled && !loading) {
          e.preventDefault();
          onClick && onClick(e);
        }
      }}
      aria-label={ariaLabel}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <>
          <i className="fas fa-spinner fa-spin" aria-hidden="true"></i>
          <span>{children || 'Cargando...'}</span>
          <span className="sr-only">Cargando, por favor espere</span>
        </>
      ) : (
        <>
          {icon && <i className={icon} aria-hidden="true"></i>}
          {children}
        </>
      )}
    </button>
  );
}
