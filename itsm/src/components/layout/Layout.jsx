import { Outlet } from 'react-router-dom'
import Header from './Header'
import ChatSidebar from '../chat/ChatSidebar'
import { useChat } from '../../context/ChatContext'

function Layout() {
  const { isChatOpen, chatContext, closeChat } = useChat()

  const sidebarWidth = chatContext.showContext ? '500px' : '400px'

  return (
    <div className="min-h-screen flex flex-col bg-[#ffffff] relative overflow-x-hidden">
      <div 
        className="flex-1 flex flex-col transition-all duration-[300ms] ease"
        style={{ 
          marginRight: isChatOpen ? sidebarWidth : '0px'
        }}
      >
        <Header />
        <Outlet />
      </div>
      <ChatSidebar 
        isOpen={isChatOpen} 
        onClose={closeChat}
        showContext={chatContext.showContext}
        showSuggestions={chatContext.showSuggestions}
        showUser={chatContext.showUser}
        placeholder={chatContext.placeholder}
        placeholderText={chatContext.placeholderText}
      />
    </div>
  )
}

export default Layout