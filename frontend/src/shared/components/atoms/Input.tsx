import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Error message to display */
  error?: string;
  /** Helper text */
  helperText?: string;
}

/**
 * Input: Reusable input field with error and helper text
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ error, helperText, className = '', ...props }, ref) => {
    const baseStyles =
      'w-full px-3 py-2 border rounded transition-colors duration-200 focus:outline-none focus:ring-2';
    const errorStyles = error ? 'border-red-500 focus:ring-red-300' : 'border-gray-300 focus:ring-blue-300';

    return (
      <div className="w-full">
        <input
          ref={ref}
          className={`${baseStyles} ${errorStyles} ${className}`.trim()}
          {...props}
        />
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
        {helperText && !error && <p className="text-sm text-gray-500 mt-1">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
