import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import ChatSidebar from '../chat/ChatSidebar'
import { useChat } from '../../context/ChatContext'

function Layout() {
  const { isChatOpen, chatContext, closeChat } = useChat()
  const [sidebarWidth, setSidebarWidth] = useState('30vw')
  const [isResizing, setIsResizing] = useState(false)

  return (
    <div className="min-h-screen flex flex-col bg-[#ffffff] relative overflow-x-hidden">
      <div 
        className="flex-1 flex flex-col"
        style={{ 
          marginRight: isChatOpen ? sidebarWidth : '0px',
          transition: isResizing ? 'none' : 'margin-right 0.3s ease'
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
        onWidthChange={setSidebarWidth}
        onResizingChange={setIsResizing}
      />
    </div>
  )
}

export default Layout