function Badge({ children, variant = 'status', className = '', showDot = false }) {
  if (variant === 'grounded') {
    return <span className={`grounded-tag ${className}`}>{children}</span>
  }

  if (variant === 'source') {
    return (
      <div className={`card-source-badge ${className}`}>
        <span>{children}</span>
      </div>
    )
  }

  return (
    <span className={`status-badge ${className}`}>
      {showDot && <span className="status-dot"></span>}
      {children}
    </span>
  )
}

export default Badge