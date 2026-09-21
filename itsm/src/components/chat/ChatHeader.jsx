import Avatar from '../shared/Avatar'

function ChatHeader({ onClose, showUser = false }) {
  return (
    <div className="chat-header">
      <div className="chat-brand">
        <div className="lambda-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M4 4L12 20L20 4" stroke="#1c1c1c" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <div className="brand-text">
          <div className="brand-name">Lambda</div>
          <div className="brand-subtitle">Contextual support assistant</div>
        </div>
      </div>
      <div className="chat-header-right">
        {showUser && (
          <div className="chat-user-profile">
            <Avatar initials="AR" size="md" />
          </div>
        )}
        <button onClick={onClose} className="chat-close-btn">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12M4 4L12 12" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>
    </div>
  )
}

export default ChatHeader