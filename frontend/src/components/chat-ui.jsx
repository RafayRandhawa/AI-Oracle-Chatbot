import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown"; // Renders markdown text into HTML
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"; // Syntax highlighting for code
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"; // One Dark code style
import toast, { Toaster } from "react-hot-toast"; // Toast notifications for feedback
import InputArea from "./input-area";
import { useTheme } from "./theme-context";
import { sendToN8n } from "../services/chatApi";
import remarkGfm from "remark-gfm"; // Enable GitHub-flavored markdown (tables, etc.)

export default function ChatUI() {
  // Messages shown in the chat. We persist them in localStorage to keep
  // history across refreshes.
  const [messages, setMessages] = useState(() => {
    return JSON.parse(localStorage.getItem("chat-history")) || [];
  });

  // Controlled input state for the message field.
  const [input, setInput] = useState("");

  // Tracks when we are waiting for the assistant response.
  const [isStreaming, setIsStreaming] = useState(false);

  // Used to auto-scroll to the latest message when messages change.
  const messagesEndRef = useRef(null);

  // Read current theme so we can apply theme-aware classes without relying
  // solely on Tailwind dark: classes.
  const { theme } = useTheme();

  // Persist chat history and auto-scroll when messages update.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    localStorage.setItem("chat-history", JSON.stringify(messages));
  }, [messages]);

  // Sends the current input to the backend (n8n) and shows the result.
  const sendMessage = async () => {
    if (!input.trim()) {
      toast.error("Please enter a message!");
      return;
    }

    // 1) Add the user message to the chat immediately for responsiveness.
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // 2) Add a placeholder assistant message that we'll replace when the
    //    backend responds.
    const assistantIndex = messages.length + 1; // position after user message
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    setIsStreaming(true);

    try {
      // 3) Call your n8n webhook to get markdown back.
      const markdown = await sendToN8n(userMessage.content);

      // 4) Replace the placeholder assistant message with the markdown.
      setMessages((prev) => {
        const updated = [...prev];
        updated[assistantIndex] = { role: "assistant", content: markdown };
        return updated;
      });
    } catch (err) {
      // If something goes wrong, notify the user and insert a friendly fallback.
      toast.error(err.message || "Failed to fetch response");
      setMessages((prev) => {
        const updated = [...prev];
        updated[assistantIndex] = { role: "assistant", content: "Sorry, I couldn't get a response." };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  // Theme-aware container classes for the chat area.
  const containerClasses = `flex flex-col h-screen ${
    theme === 'dark' ? 'bg-[#121212] text-white' : 'bg-white text-black'
  }`;

  return (
    <div className={containerClasses}>
      {/* Toast notification container */}
      <Toaster position="top-right" />

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => {
          // Different bubble styles for user vs assistant, with theme variants.
          const bubbleClass =
            msg.role === "user"
              ? (theme === 'dark'
                  ? "bg-[#D32F2F] text-white"
                  : "bg-red-600 text-white")
              : (theme === 'dark'
                  ? "bg-[#1E1E1E] text-gray-100"
                  : "bg-gray-100 text-gray-900");

          return (
            <div
              key={idx}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 whitespace-pre-wrap ${bubbleClass}`}
              >
                {/* Responsive wrapper so wide tables can scroll horizontally */}
                <div className="overflow-x-auto rounded-lg">
                  {/* Render markdown, enable GFM and style tables */}
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    children={msg.content}
                    components={{
                      // Syntax-highlight fenced code blocks
                      code({ inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline ? (
                          <SyntaxHighlighter
                            style={oneDark}
                            language={match ? match[1] : "plaintext"}
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
                          <code className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-200'} px-1 rounded`} {...props}>
                            {children}
                          </code>
                        );
                      },
                      // Table styling (GFM)
                      table({ children }) {
                        return (
                          <table
                            className={`w-full border-collapse text-sm ${
                              theme === 'dark'
                                ? 'bg-[#121212] text-gray-100'
                                : 'bg-white text-gray-900'
                            }`}
                          >
                            {children}
                          </table>
                        );
                      },
                      thead({ children }) {
                        return (
                          <thead
                            className={
                              theme === 'dark'
                                ? 'bg-[#171717]'
                                : 'bg-gray-200'
                            }
                          >
                            {children}
                          </thead>
                        );
                      },
                      tr({ children }) {
                        return (
                          <tr
                            className={`${
                              theme === 'dark'
                                ? 'odd:bg-[#161616] even:bg-[#141414]'
                                : 'odd:bg-gray-50 even:bg-white'
                            }`}
                          >
                            {children}
                          </tr>
                        );
                      },
                      th({ children }) {
                        return (
                          <th
                            className={`px-4 py-2 font-semibold text-left border ${
                              theme === 'dark'
                                ? 'border-[#2A2A2A] text-gray-200'
                                : 'border-gray-200 text-gray-700'
                            }`}
                          >
                            {children}
                          </th>
                        );
                      },
                      td({ children }) {
                        return (
                          <td
                            className={`px-4 py-2 align-top border ${
                              theme === 'dark'
                                ? 'border-[#2A2A2A]'
                                : 'border-gray-200'
                            }`}
                          >
                            {children}
                          </td>
                        );
                      },
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}

        {/* Dummy div for auto-scrolling to the latest message */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area (theme-aware) */}
      <InputArea
        input={input}
        setInput={setInput}
        isStreaming={isStreaming}
        sendMessage={sendMessage}
      />
    </div>
  );
}
