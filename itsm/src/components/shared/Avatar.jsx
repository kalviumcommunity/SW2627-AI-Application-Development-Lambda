function Avatar({ initials, name, size = 'md', className = '' }) {
  if (size === 'sm') {
    return (
      <div className={`assignment-avatar ${className}`}>
        {initials || name?.charAt(0)?.toUpperCase() || '?'}
      </div>
    )
  }
  if (size === 'activity') {
    return (
      <div className={`activity-avatar ${className}`}>
        {initials || name?.charAt(0)?.toUpperCase() || '?'}
      </div>
    )
  }
  return (
    <div className={`user-avatar ${className}`}>
      {initials || name?.charAt(0)?.toUpperCase() || '?'}
    </div>
  )
}

export default Avatar