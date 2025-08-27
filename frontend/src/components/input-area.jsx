import { useTheme } from './theme-context.jsx';

export default function InputArea({ input, setInput, isStreaming, sendMessage }){
  const { theme } = useTheme();

  const wrapperClasses = theme === 'dark'
    ? 'flex border-t border-[#2A2A2A] p-3 bg-[#121212]'
    : 'flex border-t border-gray-100 p-3 bg-white';

  const inputClasses = theme === 'dark'
    ? 'flex-1 rounded-lg p-2 text-white bg-[#1E1E1E] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#D32F2F]'
    : 'flex-1 rounded-lg p-2 text-black bg-gray-300 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-600';

  const buttonClasses = theme === 'dark'
    ? 'ml-2 px-4 py-2 rounded-lg text-white bg-[#D32F2F] hover:bg-[#c62828] disabled:opacity-50'
    : 'ml-2 px-4 py-2 rounded-lg text-gray-300 bg-gray-500 hover:bg-gray-600 disabled:opacity-50';

  return(
    <div className={wrapperClasses}>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && !isStreaming && sendMessage()}
        placeholder="Type your message..."
        className={inputClasses}
        disabled={isStreaming}
      />
      <button
        onClick={sendMessage}
        disabled={isStreaming}
        className={buttonClasses}
      >
        Send
      </button>
    </div>
  );
}