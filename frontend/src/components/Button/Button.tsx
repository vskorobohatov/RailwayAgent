import React from 'react';
import './button.css';

interface ButtonProps {
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit';
}

export function Button({ children, disabled = false, loading = false, onClick, type = 'button' }: ButtonProps) {
  return (
    <button className="btn" disabled={disabled || loading} onClick={onClick} type={type}>
      {children}
    </button>
  );
}