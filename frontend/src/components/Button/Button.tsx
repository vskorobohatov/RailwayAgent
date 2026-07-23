import React from 'react';
import './button.css';

interface ButtonProps {
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ children, disabled = false, loading = false, onClick, type = 'button', variant = 'primary', size = 'md' }: ButtonProps) {
  return (
    <button className={`btn btn--${variant} btn--${size}`} disabled={disabled || loading} onClick={onClick} type={type}>
      {children}
    </button>
  );
}
