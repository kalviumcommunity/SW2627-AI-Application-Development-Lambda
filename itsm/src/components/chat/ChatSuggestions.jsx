import { useChat } from "../../context/ChatContext";
import { FiMessageSquare } from "react-icons/fi";

function ChatSuggestions() {
  const { setQuery } = useChat();

  const suggestions = [
    "Prepare a guidance document",
    "Explain the SLAs",
    "What are the next steps?",
  ];

  return (
    <div className="chat-suggestions">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          className="suggestion-btn flex items-center gap-1.5 hover:border-[#1c1c1c] hover:bg-[#f5f5f5] transition-all"
          onClick={() => setQuery(suggestion)}
        >
          <FiMessageSquare className="w-3 h-3 text-[#666]" />
          <span>{suggestion}</span>
        </button>
      ))}
    </div>
  );
}

export default ChatSuggestions;

