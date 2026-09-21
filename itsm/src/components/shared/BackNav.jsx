import { Link } from 'react-router-dom'

function BackNav({ to, text = 'Back to incidents', className = '' }) {
  return (
    <div className={`back-nav ${className}`}>
      <Link to={to} className="back-link">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        {text}
      </Link>
    </div>
  )
}

export default BackNav