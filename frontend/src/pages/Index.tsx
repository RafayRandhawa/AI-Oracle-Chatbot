import { useMemo, useState } from "react";
import ChatWindow from "@/components/chat/ChatWindow";
import InputBar from "@/components/chat/InputBar";
import ThemeToggle from "@/components/chat/ThemeToggle";
import { ThemeProvider } from "@/hooks/use-theme";
import { ChatMessage } from "@/types/chat";
import { sendQuery } from "@/lib/api";

/**
 * Main chat interface for the Oracle Database Chatbot.
 * 
 * This component manages the chat state and coordinates between:
 * - User input (via InputBar)
 * - Message display (via ChatWindow) 
 * - Backend API communication (via sendQuery)
 * - Theme management (via ThemeProvider)
 */

const Index = () => {
  const initialMessages: ChatMessage[] = useMemo(
    () => [
      { id: "m1", role: "bot", content: "Hi! I’m your Oracle database assistant. How can I help?", timestamp: Date.now() - 100000 },
      { id: "m2", role: "user", content: "What’s the difference between a schema and a user?", timestamp: Date.now() - 90000 },
      { id: "m3", role: "bot", content: "In Oracle, a user owns a schema. The schema is the collection of objects (tables, views, etc.) owned by that user.", timestamp: Date.now() - 85000 }
    ],
    []
  );

  // Chat message history - starts with example conversation
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  
  // Tracks in-flight request to disable the input and avoid duplicate sends
  // This prevents users from sending multiple messages while waiting for a response
  const [isSending, setIsSending] = useState(false);

  /**
   * Sends user's prompt to the backend, appends server response as a bot message,
   * and provides basic error feedback if the request fails.
   * 
   * Flow:
   * 1. Immediately add user message to chat (for instant feedback)
   * 2. Set loading state to disable input
   * 3. Send request to backend API
   * 4. Add bot response or error message to chat
   * 5. Re-enable input for next message
   */
  const handleSend = async (text: string) => {
    // Add user message immediately for responsive UI
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      setIsSending(true);
      // Send to backend and wait for response
      const response = await sendQuery(text);
      
      // Create bot message with formatted response
      const botMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "bot",
        content: formatBackendResponse(response),
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error: unknown) {
      // Handle any errors (network, API, etc.) by showing error message
      const botError: ChatMessage = {
        id: crypto.randomUUID(),
        role: "bot",
        content: error instanceof Error ? error.message : "Something went wrong",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, botError]);
    } finally {
      // Always re-enable input, regardless of success/failure
      setIsSending(false);
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col bg-background">
        {/* Fixed header with app title and theme toggle */}
        <header className="fixed top-0 left-0 right-0 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="max-w-3xl mx-auto h-16 px-4 flex items-center justify-between">
            <h1 className="text-lg sm:text-xl font-semibold">Oracle Database Chatbot</h1>
            <ThemeToggle />
          </div>
        </header>

        {/* Main chat area - scrollable message history */}
        <main className="flex-1">
          <ChatWindow messages={messages} />
        </main>

        {/* Disable while awaiting backend response to prevent multiple submissions */}
        <InputBar onSend={handleSend} disabled={isSending} />
      </div>
    </ThemeProvider>
  );
};

export default Index;

/**
 * Formats backend response for simple text rendering in the chat stream.
 * Shows the generated SQL and a pretty-printed results payload.
 * 
 * The backend returns:
 * - generated_sql: The SQL query that was generated from the user's prompt
 * - results: The actual data returned from executing the SQL query
 * 
 * This function combines both into a readable format for the chat interface.
 */
function formatBackendResponse(res: { generated_sql: string; results: unknown }): string {
  try {
    // Handle both string and object results gracefully
    const resultsPretty = typeof res.results === "string" ? res.results : JSON.stringify(res.results, null, 2);
    return `SQL:\n${res.generated_sql}\n\nResults:\n${resultsPretty}`;
  } catch {
    // Fallback if JSON.stringify fails (e.g., circular references)
    return `SQL:\n${res.generated_sql}\n\nResults: [unprintable]`;
  }
}
