function ChatSuggestions() {
  const suggestions = [
    'Prepare a guidance document',
    'Explain the SLAs',
    'What are the next steps?',
  ]

  return (
    <div className="chat-suggestions">
      {suggestions.map((suggestion, index) => (
        <button key={index} className="suggestion-btn">
          {suggestion}
        </button>
      ))}
    </div>
  )
}

export default ChatSuggestions