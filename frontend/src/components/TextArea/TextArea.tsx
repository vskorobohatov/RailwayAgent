import React from 'react';
import './textarea.css';

interface TextAreaProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  rows?: number;
}

export function TextArea({ value, onChange, placeholder, disabled = false, rows = 4 }: TextAreaProps) {
  return (
    <textarea
      className="text-area"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      rows={rows}
    />
  );
}