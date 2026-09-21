function Button({ children, variant = 'primary', className = '', ...props }) {
  const baseStyles = 'px-[20px] py-[10px] rounded-[6px] font-medium text-[14px] transition-all duration-[150ms] ease cursor-pointer border outline-none inline-flex items-center justify-center gap-[8px]'
  
  const variants = {
    primary: 'bg-[#1c1c1c] text-white border-[#1c1c1c] hover:bg-[#333] hover:border-[#333]',
    secondary: 'bg-white text-[#1c1c1c] border-[#e8e8e8] hover:bg-[#f5f5f5] hover:border-[#1c1c1c]',
    'card-action': 'bg-white text-[#1c1c1c] border-[#e8e8e8] hover:bg-[#1c1c1c] hover:text-white hover:border-[#1c1c1c]',
    icon: 'bg-none border-none p-[8px] hover:bg-[#f5f5f5]',
    link: 'bg-none border-none p-0 text-[#1c1c1c] hover:underline',
  }

  return (
    <button className={`${baseStyles} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}

export default Button