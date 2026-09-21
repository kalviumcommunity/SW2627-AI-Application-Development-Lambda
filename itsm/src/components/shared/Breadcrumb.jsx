function Breadcrumb({ children, className = '' }) {
  return (
    <div className={`text-[12px] text-[#999] mb-[8px] tracking-[0.5px] uppercase ${className}`}>
      {children}
    </div>
  )
}

export default Breadcrumb