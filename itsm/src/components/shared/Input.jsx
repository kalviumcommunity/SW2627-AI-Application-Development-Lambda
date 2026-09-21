function Input({ type = 'text', placeholder = '', className = '', icon = null, ...props }) {
  if (icon) {
    return (
      <div className="search-wrapper">
        <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5.5" stroke="#666" strokeWidth="1.5"/>
          <path d="M11 11L14 14" stroke="#666" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <input
          type={type}
          placeholder={placeholder}
          className={`search-input ${className}`}
          {...props}
        />
      </div>
    )
  }

  return (
    <input
      type={type}
      placeholder={placeholder}
      className={`search-input ${className}`}
      {...props}
    />
  )
}

export default Input