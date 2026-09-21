function ChatInput({ placeholder = 'Ask about this incident...', disabled = false }) {
  return (
    <div className="chat-input-area">
      <input
        type="text"
        placeholder={placeholder}
        disabled={disabled}
        className="chat-input"
      />
      <button disabled={disabled} className="chat-submit-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 8L14 2L8 14L6.5 8.5L2 8Z" stroke="#1c1c1c" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  )
}

export default ChatInput