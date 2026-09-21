import { Link, useLocation } from 'react-router-dom'

function NavLink({ to, children, className = '' }) {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <Link
      to={to}
      className={`nav-link ${isActive ? 'active' : ''} ${className}`}
    >
      {children}
    </Link>
  )
}

export default NavLink