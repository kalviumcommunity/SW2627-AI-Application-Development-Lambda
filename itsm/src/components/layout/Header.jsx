import NavLink from '../shared/NavLink'

function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <div className="brand-name">
          Lambda<span id="itsm">ITSM</span>
        </div>
        <nav className="nav">
          <NavLink to="/">Incidents</NavLink>
          <NavLink to="/knowledge">Knowledge</NavLink>
        </nav>
      </div>
      <div className="header-right">
        <div className="user-profile">
          <div className="user-avatar">
            <img 
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%231c1c1c'/%3E%3Ctext x='16' y='21' text-anchor='middle' fill='white' font-size='12' font-family='sans-serif'%3EAR%3C/text%3E%3C/svg%3E" 
              alt="User avatar" 
            />
          </div>
          <div className="user-info">
            <div className="user-name">AR</div>
            <div className="user-role">Alex Rivera</div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header