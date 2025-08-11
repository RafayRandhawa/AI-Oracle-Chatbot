import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown"; // Renders markdown text into HTML
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"; // Syntax highlighting for code
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"; // One Dark code style
import toast, { Toaster } from "react-hot-toast"; // Toast notifications for feedback
import InputArea from "./input-area";

export default function ChatUI() {
  // =======================
  // STATE MANAGEMENT
  // =======================

  // Messages state — loads from localStorage if available
  const [messages, setMessages] = useState(() => {
    return JSON.parse(localStorage.getItem("chat-history")) || [];
  });

  // Input field text
  const [input, setInput] = useState("");

  // Boolean to track if assistant is "typing" / streaming
  const [isStreaming, setIsStreaming] = useState(false);

  // Ref to scroll to the bottom when a new message arrives
  const messagesEndRef = useRef(null);

  // =======================
  // EFFECTS
  // =======================

  useEffect(() => {
    // Scroll to the last message whenever messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

    // Save chat history to localStorage so it persists on refresh
    localStorage.setItem("chat-history", JSON.stringify(messages));
  }, [messages]);

  // =======================
  // SEND MESSAGE FUNCTION
  // =======================

  const sendMessage = () => {
    // Show error toast if user tries to send empty message
    if (!input.trim()) {
      toast.error("Please enter a message!");
      return;
    }

    // Add user message to chat
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput(""); // Clear input field

    // Prepare an empty assistant message for streaming
    const assistantMessage = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMessage]);
    setIsStreaming(true);

    // =======================
    // SIMULATED STREAMING RESPONSE
    // (Replace this with real backend streaming later)
    // =======================
    const fakeResponse =
      "Hello! This is a simulated AI typing effect.\n\n```js\nconsole.log('Hello World');\n```";

    let index = 0; // Tracks which character we're adding
    let buffer = ""; // Holds the growing text

    // Simulate AI typing by adding one character at a time
    const streamInterval = setInterval(() => {
      if (index < fakeResponse.length) {
        buffer += fakeResponse[index]; // Append next character

        // Update the *last* message (assistant's) in state
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: buffer,
          };
          return updated;
        });

        index++; // Move to next character
      } else {
        // Stop streaming when done
        clearInterval(streamInterval);
        setIsStreaming(false);
      }
    }, 25); // Typing speed (ms per character)
  };

  // =======================
  // RENDER
  // =======================
  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Toast notification container */}
      <Toaster position="top-right" />

      {/* =======================
          MESSAGES LIST
      ======================= */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap ${
                msg.role === "user" ? "bg-blue-500" : "bg-gray-400"
              }`}
            >
              {/* Render markdown with syntax highlighting */}
              <ReactMarkdown
                children={msg.content}
                components={{
                  code({ inline, className, children, ...props }) {
                    // Detect language from markdown code fence (```js)
                    const match = /language-(\w+)/.exec(className || "");

                    return !inline ? (
                      // Syntax highlighting for code blocks
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match ? match[1] : "plaintext"} // Default to plaintext if no match
                        PreTag="div"
                        customStyle={{
                          background: "#1e1e1e",
                          borderRadius: "0.5rem",
                          padding: "0.75rem",
                          whiteSpace: "pre-wrap",
                          wordBreak: "break-word",
                        }}
                        {...props}
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    ) : (
                      // Inline code styling
                      <code className="bg-gray-800 px-1 rounded" {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              />
            </div>
          </div>
        ))}

        {/* Dummy div for auto-scrolling */}
        <div ref={messagesEndRef} />
      </div>

      {/* =======================
          INPUT AREA
      ======================= */}
      <InputArea></InputArea>
    </div>
  );
}
