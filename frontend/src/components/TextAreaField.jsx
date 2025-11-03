import React, { useState, useEffect } from 'react';

export function TextAreaField({ 
  label, 
  id, 
  value, 
  onChange, 
  placeholder, 
  helpText, 
  maxLength = 1000,
  minLength = 10,
  showCounter = true,
  required = false,
  error = null,
  rows = 4,
  className = '',
  onValidationChange,
  ...props 
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const [validationSuccess, setValidationSuccess] = useState(false);
  
  const handleMouseEnter = () => setShowTooltip(true);
  const handleMouseLeave = () => setShowTooltip(false);

  // Validación en tiempo real
  useEffect(() => {
    const trimmedValue = (value || '').trim();
    let errorMessage = null;
    let isValid = true;

    if (required && trimmedValue.length === 0) {
      errorMessage = 'Este campo es obligatorio';
      isValid = false;
    } else if (trimmedValue.length > 0 && trimmedValue.length < minLength) {
      errorMessage = `Mínimo ${minLength} caracteres requeridos`;
      isValid = false;
    } else if (trimmedValue.length > maxLength) {
      errorMessage = `Máximo ${maxLength} caracteres permitidos`;
      isValid = false;
    } else if (trimmedValue.length >= minLength) {
      isValid = true;
      setValidationSuccess(true);
    }

    setValidationError(errorMessage);
    setValidationSuccess(isValid && trimmedValue.length >= minLength);

    // Notificar al componente padre del estado de validación
    if (onValidationChange) {
      onValidationChange(isValid && trimmedValue.length >= minLength);
    }
  }, [value, minLength, maxLength, required, onValidationChange]);

  const getCounterClass = () => {
    if (value.length > maxLength) return 'error';
    if (value.length > maxLength * 0.9) return 'warning';
    return '';
  };

  const getInputClass = () => {
    let classes = '';
    if (validationError) classes += ' error';
    if (validationSuccess && !validationError) classes += ' success';
    if (error) classes += ' error';
    return classes.trim();
  };

  const displayError = error || validationError;

  return (
    <div className={`form-group textarea-group ${className} ${displayError ? 'error' : ''} ${validationSuccess ? 'success' : ''}`}>
      <label htmlFor={id} className="form-label">
        {label}
        {required && <span className="required">*</span>}
        {helpText && (
          <div className="help-trigger" onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
            <i className="fas fa-info-circle"></i>
            {showTooltip && (
              <div className="tooltip">
                <div className="tooltip-content">
                  {helpText}
                </div>
                <div className="tooltip-arrow"></div>
              </div>
            )}
          </div>
        )}
      </label>
      
      <div className="textarea-wrapper">
        <textarea
          id={id}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          maxLength={maxLength}
          required={required}
          rows={rows}
          className={`form-control textarea ${getInputClass()}`}
          {...props}
        />
        
        {showCounter && (
          <div className="char-counter">
            <span className={getCounterClass()}>
              {value.length}/{maxLength}
            </span>
            {value.length > 0 && value.length < minLength && (
              <span className="counter-warning">
                <i className="fas fa-info-circle"></i>
                Mínimo {minLength} caracteres
              </span>
            )}
            {value.length > maxLength * 0.9 && value.length <= maxLength && (
              <span className="counter-warning">
                <i className="fas fa-exclamation-triangle"></i>
                Cerca del límite
              </span>
            )}
            {validationSuccess && (
              <span className="counter-success">
                <i className="fas fa-check-circle"></i>
                Válido
              </span>
            )}
          </div>
        )}
      </div>
      
      {displayError && (
        <div className="field-error">
          <i className="fas fa-exclamation-circle"></i>
          {displayError}
        </div>
      )}
      
      {validationSuccess && !displayError && (
        <div className="field-success">
          <i className="fas fa-check-circle"></i>
          Campo válido
        </div>
      )}
    </div>
  );
}
