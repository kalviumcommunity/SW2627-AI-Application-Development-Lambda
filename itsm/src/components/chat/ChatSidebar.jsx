import { useEffect } from 'react'
import ChatHeader from './ChatHeader'
import ChatContent from './ChatContent'
import ChatInput from './ChatInput'
import ChatSuggestions from './ChatSuggestions'

function ChatSidebar({ isOpen, onClose, showContext = false, showSuggestions = false, showUser = false, placeholder = 'Ask about incidents...', placeholderText = 'Start a conversation to get assistance' }) {
  const sidebarWidth = '50vw'

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <div 
      className={`chat-sidebar ${isOpen ? 'open' : ''}`}
      style={{ 
        width: sidebarWidth,
        right: isOpen ? '0' : `-${sidebarWidth}`
      }}
    >
      <ChatHeader onClose={onClose} showUser={showUser} />
      <ChatContent placeholderText={placeholderText} />
      {showSuggestions && <ChatSuggestions />}
      <ChatInput placeholder={placeholder} />
    </div>
  )
}

export default ChatSidebar