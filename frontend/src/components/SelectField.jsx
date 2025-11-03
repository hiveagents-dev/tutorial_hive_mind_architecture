import React, { useState } from 'react';

export function SelectField({ 
  label, 
  id, 
  value, 
  onChange, 
  options = [],
  helpText, 
  required = false,
  error = null,
  className = '',
  ...props 
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const handleMouseEnter = () => setShowTooltip(true);
  const handleMouseLeave = () => setShowTooltip(false);

  return (
    <div className={`form-group select-group ${className} ${error ? 'error' : ''}`}>
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
      
      <div className="select-wrapper">
        <select
          id={id}
          value={value}
          onChange={onChange}
          required={required}
          className={`form-control select ${error ? 'error' : ''}`}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <i className="fas fa-chevron-down select-icon"></i>
      </div>
      
      {error && (
        <div className="field-error">
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </div>
      )}
    </div>
  );
}
