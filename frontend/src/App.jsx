import React, { useState, useEffect, useRef, use } from 'react';
import { ThemeProvider, useTheme } from './components/theme-context.jsx';
import ChatUI from './components/chat-ui.jsx';
import ThemeSwitch from './components/theme-switch.jsx';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/login";
import { AuthProvider } from './auth/authContext.jsx';
import { Sidebar, SidebarBody, SidebarLink } from './components/ui/sidebar.jsx';
import {
  IconArrowLeft,
  IconBrandTabler,
  IconSettings,
  IconUserBolt,
} from "@tabler/icons-react";

import { getSessions, getMessages } from "./services/sessions";

export default function App() {
  const [open, setOpen] = useState(false);
  const [chatSessions, setChatSessions] = useState([]);
  const [error, setError] = useState(null); // Track errors
  const [messages, setMessages] = useState([]);
  const sidebarRef = useRef(null);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  
  useEffect(() => {
    const hash = window.location.hash; // e.g., "#session-123"
    if (hash.startsWith("#session-")) {
      const sessionId = hash.split("-")[1]; // Extract "123"
      setCurrentSessionId(sessionId);
     
    }
  }, []);

  useEffect(() => {
    async function fetchMessages(sessionId) {
      try {
        
        const data = await getMessages(sessionId);
        console.log("Fetched messages for session", sessionId, data);
        setMessages(data);
      } catch (err) {
        console.error("Failed to fetch messages:", err);
      }
    }

    // Only fetch messages if we have a valid session ID
    if (currentSessionId) {
      fetchMessages(currentSessionId);
    } else {
      // Clear messages when no session is selected
      setMessages([]);
    }
  }, [currentSessionId])

  useEffect(() => {
    async function fetchSessions() {
      try {
        const sessions = await getSessions();
        setChatSessions(sessions);
      } catch (err) {
        console.error("Failed to fetch sessions:", err);
        setError("Failed to load chat sessions."); // Set error message
      }
    }

    fetchSessions();
  }, []);

  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/chat" element={
              <div className="flex h-screen">
                <Sidebar ref={sidebarRef} open={open} setOpen={setOpen} animate={false} className="w-1/4">
                  <SidebarBody className="justify-between gap-10">
                    <div className="flex flex-1 flex-col overflow-x-hidden overflow-y-auto">
                      {/* New Chat button at the top */}
                      <div className="mt-4 mb-2">
                        <SidebarLink
                          link={{
                            label: "New Chat",
                            href: "#",
                            icon: (
                              <IconUserBolt className="h-5 w-5 shrink-0 text-neutral-700 dark:text-neutral-200" />
                            ),
                          }}
                          onClick={() => {
                            // Clear messages & start new session
                          
                            setMessages([]);
                            setCurrentSessionId(null);
                            console.log("🆕 New chat started!");
                          }}
                        />
                      </div>
                      {/* List of chat sessions */}
                      <div className="mt-8 flex flex-col gap-2">
                        {error ? (
                          <div className="error-message">{error}</div> // Display error message
                        ) : chatSessions.length > 0 ? (
                          chatSessions.map((session) => (
                            <SidebarLink
                              key={session.id}
                              link={{
                                label: session.name, // Display the name of the chat session
                                href: `#session-${session.id}`, // Link to the specific chat session
                                icon: (
                                  <IconBrandTabler className="h-5 w-5 shrink-0 text-neutral-700 dark:text-neutral-200" />
                                ),
                              }}
                            />
                          ))
                        ) : (
                          <div>No chat sessions available.</div> // Fallback content
                        )}
                      </div>
                    </div>
                    {/* Account section at the bottom of the sidebar */}
                    <div className="border-t border-neutral-300 dark:border-neutral-700 pt-4">
                      {/* User name and avatar */}
                      <SidebarLink
                        link={{
                          label: "User Name",
                          href: "#",
                          icon: (
                            <img
                              src="https://placehold.co/300x300?text=L"
                              className="h-7 w-7 shrink-0 rounded-full"
                              width={50}
                              height={50}
                              alt="Avatar"
                            />
                          ),
                        }}
                      />
                      {/* Logout option */}
                      <SidebarLink
                        link={{
                          label: "Logout",
                          href: "#logout",
                          icon: (
                            <IconArrowLeft className="h-5 w-5 shrink-0 text-neutral-700 dark:text-neutral-200" />
                          ),
                        }}
                      />
                    </div>
                    {/* Conditionally render ThemeSwitch */}

                    <div>
                      <ThemeSwitch />
                    </div>

                  </SidebarBody>
                </Sidebar>
                <div className="flex-1">
                  <ChatUI
                    messages={messages}
                    setMessages={setMessages}
                    currentSessionId={currentSessionId}
                    setCurrentSessionId={setCurrentSessionId}
                  />
                </div>
              </div>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}
