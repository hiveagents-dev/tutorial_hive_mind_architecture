import React, { useState } from 'react';

export function FormField({ 
  label, 
  id, 
  type = 'text', 
  value, 
  onChange, 
  placeholder, 
  helpText, 
  maxLength, 
  showCounter = false,
  required = false,
  error = null,
  children,
  className = '',
  ...props 
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const handleMouseEnter = () => setShowTooltip(true);
  const handleMouseLeave = () => setShowTooltip(false);

  return (
    <div className={`form-group ${className} ${error ? 'error' : ''}`}>
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
      
      {children || (
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          maxLength={maxLength}
          required={required}
          className={`form-control ${error ? 'error' : ''}`}
          {...props}
        />
      )}
      
      {showCounter && maxLength && (
        <div className="char-counter">
          <span className={value.length > maxLength * 0.9 ? 'warning' : ''}>
            {value.length}/{maxLength}
          </span>
        </div>
      )}
      
      {error && (
        <div className="field-error">
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </div>
      )}
    </div>
  );
}
