import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import { ChatMessage } from "@/types/chat";

type Props = {
  messages: ChatMessage[];
};

const ChatWindow = ({ messages }: Props) => {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  return (
    <section
      className="flex-1 overflow-y-auto pt-16 pb-28"
      aria-live="polite"
      aria-label="Chat messages"
    >
      <div className="max-w-3xl mx-auto px-4">
        <ul className="flex flex-col gap-3">
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))}
        </ul>
        <div ref={endRef} />
      </div>
    </section>
  );
};

export default ChatWindow;
