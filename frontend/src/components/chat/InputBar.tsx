import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

type Props = {
  onSend: (text: string) => void;
  disabled?: boolean;
};

const InputBar = ({ onSend, disabled }: Props) => {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <footer
      className="fixed bottom-0 left-0 right-0 border-t border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="contentinfo"
    >
      <form
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-2"
        aria-label="Chat input form"
      >
        <label htmlFor="chat-input" className="sr-only">
          Message Oracle chatbot
        </label>
        <input
          id="chat-input"
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask about Oracle SQL, PL/SQL, tuning..."
          className="flex-1 bg-card text-foreground placeholder:text-muted-foreground border border-input rounded-full px-4 py-3 focus:outline-none focus:ring-2 focus:ring-ring transition-shadow"
          aria-label="Type your message"
        />
        <button
          type="submit"
          disabled={disabled}
          className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-4 py-3 hover:opacity-90 hover-scale disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background transition"
          aria-label="Send message"
        >
          <span className="hidden sm:inline">Send</span>
          <Send className="h-5 w-5" />
        </button>
      </form>
    </footer>
  );
};

export default InputBar;
