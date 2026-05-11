import React from 'react';
import { Input } from '../atoms/Input';
import { Label } from '../atoms/Label';

export interface FormFieldProps {
  label: string;
  name: string;
  error?: string;
  helperText?: string;
  type?: string;
  placeholder?: string;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
}

/**
 * FormField: Molecule combining Label + Input + error message
 */
export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  error,
  helperText,
  required,
  ...inputProps
}) => (
  <div className="mb-4">
    <Label htmlFor={name}>
      {label} {required && <span className="text-red-500">*</span>}
    </Label>
    <Input id={name} name={name} error={error} helperText={helperText} {...inputProps} />
  </div>
);

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: React.ReactNode;
}

/**
 * Card: Container component with optional title
 */
export const Card: React.FC<CardProps> = ({ title, children, className = '', ...props }) => (
  <div className={`bg-white rounded-lg shadow-md p-4 ${className}`.trim()} {...props}>
    {title && <h2 className="text-lg font-semibold mb-4 text-gray-800">{title}</h2>}
    {children}
  </div>
);

/**
 * LoadingSpinner: Animated loading indicator
 */
export const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

/**
 * ErrorMessage: Error display component
 */
export const ErrorMessage: React.FC<{ message: string }> = ({ message }) => (
  <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded text-red-700">
    <span className="text-xl">⚠️</span>
    <span>{message}</span>
  </div>
);

/**
 * SuccessMessage: Success display component
 */
export const SuccessMessage: React.FC<{ message: string }> = ({ message }) => (
  <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded text-green-700">
    <span className="text-xl">✓</span>
    <span>{message}</span>
  </div>
);
