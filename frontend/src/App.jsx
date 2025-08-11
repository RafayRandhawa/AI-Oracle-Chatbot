import React from 'react';
import { ThemeProvider, useTheme } from './components/theme-context.jsx';
import ChatUI from './components/chat-ui.jsx';

function ThemeToggleButton() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      onClick={toggleTheme}
      className="px-4 py-2 rounded-md font-bold transition-colors
                 bg-darkAccent text-white hover:bg-red-700 dark:bg-darkAccent"
    >
      Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode
    </button>
  );
}

function Content() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center
                    bg-white text-black dark:bg-darkBg dark:text-white">
      <h1 className="text-4xl mb-6 dark:text-darkAccent">Hello, Red + Black Dark Mode!</h1>
      <ThemeToggleButton />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <Content />
      <ChatUI></ChatUI>
    </ThemeProvider>
  );
}
