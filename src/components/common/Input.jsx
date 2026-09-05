import React, { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

export default function Input({
  label,
  type = 'text',
  error,
  helperText,
  icon: Icon,
  className = '',
  id,
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  ...props
}) {
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type

  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

  return (
    <div className="w-full space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-walnut-700">
          {label} {required && <span className="text-dustyrose">*</span>}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-3.5 text-softgray pointer-events-none">
            <Icon className="w-4 h-4" />
          </div>
        )}

        <input
          id={inputId}
          type={inputType}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`w-full text-xs p-3 ${Icon ? 'pl-9' : 'pl-3.5'} ${
            isPassword ? 'pr-9' : 'pr-3.5'
          } bg-cream-100 border rounded-xl text-charcoal placeholder:text-softgray transition-all focus:outline-none focus:ring-2 focus:ring-walnut-500 ${
            error ? 'border-dustyrose ring-1 ring-dustyrose' : 'border-walnut-200/80 focus:border-walnut-500'
          } ${disabled ? 'bg-cream-200 text-softgray cursor-not-allowed' : ''} ${className}`}
          {...props}
        />

        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-3.5 text-softgray hover:text-walnut-800"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>

      {error && <p className="text-[11px] font-semibold text-dustyrose mt-0.5">{error}</p>}
      {helperText && !error && <p className="text-[10px] text-softgray mt-0.5">{helperText}</p>}
    </div>
  )
}
