function Card({ children, className = '', hoverable = false }) {
  return (
    <div className={`border border-[#e8e8e8] rounded-[8px] bg-white ${hoverable ? 'transition-all duration-[150ms] ease hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)] hover:border-[#1c1c1c]' : ''} ${className}`}>
      {children}
    </div>
  )
}

export default Card