function LambdaLogo({ size = 24, className = '' }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
    >
      <path 
        d="M4 4L12 20L20 4" 
        stroke="#1c1c1c" 
        strokeWidth="3" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default LambdaLogo