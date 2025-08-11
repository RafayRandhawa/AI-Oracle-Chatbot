export default function InputArea(){

    return(
        <div className="flex border-t border-gray-700 p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isStreaming && sendMessage()}
          placeholder="Type your message..."
          className="flex-1 bg-gray-800 rounded-lg p-2 text-white outline-none"
          disabled={isStreaming}
        />
        <button
          onClick={sendMessage}
          disabled={isStreaming}
          className="ml-2 bg-blue-600 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          Send
        </button>
      </div>
    );
}