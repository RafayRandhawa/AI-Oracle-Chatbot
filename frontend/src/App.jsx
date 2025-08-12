import React from 'react';
import { ThemeProvider, useTheme } from './components/theme-context.jsx';
import ChatUI from './components/chat-ui.jsx';
import ThemeSwitch from './components/theme-switch.jsx';

function Navbar() {
  const { theme } = useTheme();
  const headerBase = 'sticky top-0 z-50 w-full border-b';
  const headerTheme = theme === 'dark'
    ? 'bg-[#121212] text-white border-[#2A2A2A]'
    : 'bg-gray-200 text-black border-gray-200';

  return (
    <header className={`${headerBase} ${headerTheme}`}>
      <div className="mx-auto mr-1 max-w-6xl px-4 py-3 flex items-center justify-end">
        <ThemeSwitch />
      </div>
    </header>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <ChatUI />
        </main>
      </div>
    </ThemeProvider>
  );
}
