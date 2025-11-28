import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // 从localStorage读取主题，默认为'light'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('emotional_chat_theme');
    return savedTheme || 'light';
  });

  // 切换主题
  const toggleTheme = () => {
    setTheme((prevTheme) => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      localStorage.setItem('emotional_chat_theme', newTheme);
      return newTheme;
    });
  };

  // 初始化时应用主题
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  const value = {
    theme,
    toggleTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

