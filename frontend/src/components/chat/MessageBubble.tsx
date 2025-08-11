import { ChatMessage } from "@/types/chat";
import { cn } from "@/lib/utils";

type Props = {
  message: ChatMessage;
};

const MessageBubble = ({ message }: Props) => {
  const isUser = message.role === "user";

  return (
    <li
      className={cn(
        "w-full flex animate-fade-in",
        isUser ? "justify-end" : "justify-start"
      )}
      role="article"
      aria-label={`${isUser ? "User" : "Bot"} message`}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm",
          isUser
            ? "bg-chat-user text-chat-user-foreground rounded-br-md"
            : "bg-chat-bot text-chat-bot-foreground rounded-bl-md"
        )}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
      </div>
    </li>
  );
};

export default MessageBubble;
