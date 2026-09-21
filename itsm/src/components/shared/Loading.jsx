function Loading({ type = 'thinking' }) {
  if (type === 'thinking') {
    return (
      <div className="flex items-center gap-[8px] py-[12px] px-[16px] bg-[#f5f5f5] rounded-[12px] max-w-[80px]">
        <div className="flex gap-[4px]">
          <div className="w-[6px] h-[6px] rounded-full bg-[#999] animate-thinking" style={{ animationDelay: '0s' }}></div>
          <div className="w-[6px] h-[6px] rounded-full bg-[#999] animate-thinking" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-[6px] h-[6px] rounded-full bg-[#999] animate-thinking" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>
    )
  }

  return null
}

export default Loading