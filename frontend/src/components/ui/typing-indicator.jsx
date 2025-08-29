import React from "react";

export default function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 p-2">
      <span className="flex space-x-1">
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-200 rounded-full animate-bounce"></span>
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-200 rounded-full animate-bounce delay-150"></span>
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-200 rounded-full animate-bounce delay-300"></span>
      </span>
      <span className="text-gray-500 text-sm">Bot is typing...</span>
    </div>
  );
}
