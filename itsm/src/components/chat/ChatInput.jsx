import { useEffect, useRef } from "react";
import { useChat } from "../../context/ChatContext";
import { FiSend } from "react-icons/fi";

function ChatInput({
  placeholder = "Ask about this incident...",
  disabled = false,
}) {
  const { query, setQuery, sendQuery } = useChat();
  const inputRef = useRef(null);

  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (query.trim()) {
        sendQuery();
      }
    } else if (e.key === "Escape" && query) {
      e.preventDefault();
      setQuery("");
    }
  };

  return (
    <div className="chat-input-area">
      <div className="relative flex-1 flex items-center">
        <input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          disabled={disabled}
          className="chat-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="chat-input-hints hidden sm:flex">
          <kbd>Enter ↵</kbd>
        </div>
      </div>
      <button
        disabled={disabled || !query.trim()}
        className="chat-submit-btn"
        onClick={sendQuery}
        title="Send message (Enter)"
        aria-label="Send message"
      >
        <FiSend className="w-4 h-4 text-[#1c1c1c]" />
      </button>
    </div>
  );
}

export default ChatInput;

