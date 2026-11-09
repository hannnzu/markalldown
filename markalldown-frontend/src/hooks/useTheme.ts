"use client";

import { useEffect, useState } from "react";

export type Theme = "light" | "dark" | "system";

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>("system");

  // Inisialisasi dari localStorage saat mount
  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored) setThemeState(stored);
  }, []);

  // Terapkan class ke <html> setiap kali tema berubah — FR-23, AC-21
  useEffect(() => {
    const root = document.documentElement;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    const isDark =
      theme === "dark" || (theme === "system" && prefersDark);

    root.classList.toggle("dark", isDark);
  }, [theme]);

  const setTheme = (t: Theme) => {
    setThemeState(t);
    localStorage.setItem("theme", t);
  };

  return { theme, setTheme };
}
