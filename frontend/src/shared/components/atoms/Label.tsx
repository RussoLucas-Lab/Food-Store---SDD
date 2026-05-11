import React from 'react';

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children: React.ReactNode;
}

/**
 * Label: Simple label component for form fields
 */
export const Label: React.FC<LabelProps> = ({ className = '', ...props }) => (
  <label className={`block text-sm font-medium text-gray-700 mb-1 ${className}`.trim()} {...props} />
);

Label.displayName = 'Label';

export interface TextProps extends React.HTMLAttributes<HTMLParagraphElement> {
  variant?: 'body' | 'small' | 'caption' | 'heading1' | 'heading2';
  children: React.ReactNode;
}

/**
 * Text: Typography component with variants
 */
export const Text: React.FC<TextProps> = ({ variant = 'body', className = '', ...props }) => {
  const variantStyles = {
    body: 'text-base text-gray-700',
    small: 'text-sm text-gray-600',
    caption: 'text-xs text-gray-500',
    heading1: 'text-3xl font-bold text-gray-900',
    heading2: 'text-2xl font-semibold text-gray-800',
  };

  return (
    <p className={`${variantStyles[variant]} ${className}`.trim()} {...props} />
  );
};

Text.displayName = 'Text';
