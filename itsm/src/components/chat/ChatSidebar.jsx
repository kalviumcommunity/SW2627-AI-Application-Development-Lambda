import { useState, useEffect, useRef } from 'react'
import ChatHeader from './ChatHeader'
import ChatContent from './ChatContent'
import ChatInput from './ChatInput'
import ChatSuggestions from './ChatSuggestions'

function ChatSidebar({ 
  isOpen, 
  onClose, 
  showContext = false, 
  showSuggestions = false, 
  showUser = false, 
  placeholder = 'Ask about incidents...', 
  placeholderText = 'Start a conversation to get assistance',
  onWidthChange,
  onResizingChange
}) {
  const [width, setWidth] = useState('30vw')
  const [isResizing, setIsResizing] = useState(false)
  const isResizingRef = useRef(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsResizing(true);
    isResizingRef.current = true;
    if (onResizingChange) onResizingChange(true);
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'ew-resize';
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizingRef.current) return;
      const newWidthPx = window.innerWidth - e.clientX;
      const minWidthPx = Math.max(320, window.innerWidth * 0.25);
      const maxWidthPx = window.innerWidth * 0.85;
      const clampedWidth = Math.min(Math.max(newWidthPx, minWidthPx), maxWidthPx);
      const formattedWidth = `${clampedWidth}px`;
      setWidth(formattedWidth);
      if (onWidthChange) onWidthChange(formattedWidth);
    };

    const handleMouseUp = () => {
      if (isResizingRef.current) {
        isResizingRef.current = false;
        setIsResizing(false);
        if (onResizingChange) onResizingChange(false);
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [onWidthChange, onResizingChange]);

  return (
    <div 
      className={`chat-sidebar ${isOpen ? 'open' : ''} ${isResizing ? 'resizing' : ''}`}
      style={{ 
        width: width,
        right: isOpen ? '0' : `-${width}`,
        transition: isResizing ? 'none' : 'right 0.3s ease, width 0.3s ease'
      }}
    >
      <div 
        className="resize-handle-left"
        onMouseDown={handleMouseDown}
        title="Drag left/right to resize sidebar"
      >
        <div className="resize-handle-indicator" />
      </div>
      <ChatHeader onClose={onClose} showUser={showUser} />
      <ChatContent placeholderText={placeholderText} />
      {showSuggestions && <ChatSuggestions />}
      <ChatInput placeholder={placeholder} />
    </div>
  )
}

export default ChatSidebar