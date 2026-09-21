function ChatContent({ placeholderText = 'Start a conversation to get assistance with this incident' }) {
  return (
    <div className="chat-content">
      <div className="chat-placeholder">
        <div className="placeholder-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <path d="M24 4L28 20L44 24L28 28L24 44L20 28L4 24L20 20L24 4Z" stroke="#e8e8e8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <p>AI Assistant ready to help</p>
        <p className="placeholder-subtext">{placeholderText}</p>
      </div>
    </div>
  )
}

export default ChatContent