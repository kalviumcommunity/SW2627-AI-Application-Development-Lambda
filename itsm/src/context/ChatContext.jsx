import { createContext, useContext, useState } from 'react'

const ChatContext = createContext()

export function ChatProvider({ children }) {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [chatContext, setChatContext] = useState({
    showContext: false,
    showSuggestions: false,
    showUser: false,
    placeholder: 'Ask about incidents...',
    placeholderText: 'Start a conversation to get assistance',
  })

  const openChat = (options = {}) => {
    setChatContext({
      showContext: options.showContext || false,
      showSuggestions: options.showSuggestions || false,
      showUser: options.showUser || false,
      placeholder: options.placeholder || 'Ask about incidents...',
      placeholderText: options.placeholderText || 'Start a conversation to get assistance',
    })
    setIsChatOpen(true)
  }

  const closeChat = () => {
    setIsChatOpen(false)
  }

  return (
    <ChatContext.Provider value={{ isChatOpen, chatContext, openChat, closeChat }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}