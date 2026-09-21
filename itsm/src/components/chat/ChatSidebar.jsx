import ChatHeader from './ChatHeader'
import ChatContent from './ChatContent'
import ChatInput from './ChatInput'
import ContextSection from './ContextSection'
import ChatSuggestions from './ChatSuggestions'

function ChatSidebar({ isOpen, onClose, showContext = false, showSuggestions = false, showUser = false, placeholder = 'Ask about incidents...', placeholderText = 'Start a conversation to get assistance' }) {
  const sidebarWidth = showContext ? '500px' : '400px'

  return (
    <div 
      className={`chat-sidebar ${isOpen ? 'open' : ''}`}
      style={{ 
        width: sidebarWidth,
        right: isOpen ? '0' : `-${sidebarWidth}`
      }}
    >
      <ChatHeader onClose={onClose} showUser={showUser} />
      {showContext && <ContextSection />}
      <ChatContent placeholderText={placeholderText} />
      {showSuggestions && <ChatSuggestions />}
      <ChatInput placeholder={placeholder} />
    </div>
  )
}

export default ChatSidebar