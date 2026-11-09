"use client";

import { useState } from "react";

interface UrlInputProps {
  onSubmit: (url: string) => void;
  disabled?: boolean;
}

export default function UrlInput({ onSubmit, disabled }: UrlInputProps) {
  const [value, setValue] = useState("");
  const [error, setError] = useState("");

  const validate = (url: string): boolean => {
    try {
      const u = new URL(url);
      if (u.protocol !== "http:" && u.protocol !== "https:") {
        setError("Hanya URL http:// dan https:// yang diizinkan");
        return false;
      }
    } catch {
      setError("URL tidak valid");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    if (validate(trimmed)) {
      onSubmit(trimmed);
      setValue("");
    }
  };

  return (
    <form className="url-input" onSubmit={handleSubmit} noValidate>
      <label htmlFor="url-field" className="url-input__label">
        Konversi URL / YouTube
      </label>
      <div className="url-input__row">
        <input
          id="url-field"
          type="url"
          className={`url-input__field ${error ? "url-input__field--error" : ""}`}
          placeholder="https://example.com atau https://youtube.com/watch?v=…"
          value={value}
          onChange={(e) => { setValue(e.target.value); if (error) setError(""); }}
          disabled={disabled}
          maxLength={2048}
          aria-describedby={error ? "url-error" : undefined}
          aria-invalid={!!error}
        />
        <button
          type="submit"
          className="btn btn--primary"
          disabled={disabled || !value.trim()}
        >
          Konversi
        </button>
      </div>
      {error && (
        <p id="url-error" className="url-input__error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
