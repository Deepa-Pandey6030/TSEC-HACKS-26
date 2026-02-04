import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext(undefined);

export function ThemeProvider({ 
  children, 
  defaultTheme = 'system', 
  storageKey = 'truthshield-theme' 
}) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem(storageKey) || defaultTheme;
  });
  
  const [motionPreference, setMotionPreference] = useState(() => {
    const stored = localStorage.getItem('truthshield-motion');
    if (stored) return stored;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduced' : 'full';
  });

  const [actualTheme, setActualTheme] = useState('light');

  useEffect(() => {
    const root = window.document.documentElement;
    
    root.classList.remove('light', 'dark');
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
      setActualTheme(systemTheme);
    } else {
      root.classList.add(theme);
      setActualTheme(theme);
    }

    // Apply CSS custom properties for theme
    const tokens = {
      '--shadow-sm': theme === 'dark' ? '0 1px 3px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(0, 0, 0, 0.6)' : '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
      '--shadow-md': theme === 'dark' ? '0 4px 6px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.3)' : '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
      '--shadow-lg': theme === 'dark' ? '0 10px 25px rgba(0, 0, 0, 0.6), 0 4px 12px rgba(0, 0, 0, 0.4)' : '0 10px 25px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08)',
      '--shadow-xl': theme === 'dark' ? '0 25px 50px rgba(0, 0, 0, 0.8), 0 10px 20px rgba(0, 0, 0, 0.6)' : '0 25px 50px rgba(0, 0, 0, 0.2), 0 10px 20px rgba(0, 0, 0, 0.1)',
      '--shadow-glow': theme === 'dark' ? '0 0 20px rgba(0, 217, 255, 0.5), 0 0 40px rgba(0, 217, 255, 0.2)' : '0 0 20px rgba(0, 217, 255, 0.3), 0 0 40px rgba(0, 217, 255, 0.1)',
    };
    
    Object.entries(tokens).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(storageKey, theme);
  }, [theme, storageKey]);

  useEffect(() => {
    localStorage.setItem('truthshield-motion', motionPreference);
  }, [motionPreference]);

  const isReducedMotion = motionPreference === 'reduced';

  const value = {
    theme,
    setTheme,
    actualTheme,
    motionPreference,
    setMotionPreference,
    isReducedMotion,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}