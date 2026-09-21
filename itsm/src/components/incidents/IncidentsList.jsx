import { Link } from 'react-router-dom'
import Badge from '../shared/Badge'
import Avatar from '../shared/Avatar'

function IncidentsList({ incidents }) {
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="incidents-list">
      <div className="incidents-header">
        <div className="header-cell cell-id">ID</div>
        <div className="header-cell cell-description">Description</div>
        <div className="header-cell cell-client">Client</div>
        <div className="header-cell cell-assignment">Assignment</div>
        <div className="header-cell cell-status">Status</div>
        <div className="header-cell cell-updated">Last updated</div>
      </div>
      <div className="incidents-body">
        {incidents.map((incident) => (
          <Link
            key={incident.id}
            to={`/incident/${incident.id}`}
            className="incident-row"
          >
            <div className="cell cell-id">
              {incident.id}
            </div>
            <div className="cell cell-description">
              {incident.description}
            </div>
            <div className="cell cell-client">
              {incident.client}
            </div>
            <div className="cell cell-assignment">
              <Avatar initials={getInitials(incident.assignment)} size="sm" />
              <span className="assignment-name">{incident.assignment}</span>
            </div>
            <div className="cell cell-status">
              <Badge showDot variant="status">{incident.status}</Badge>
            </div>
            <div className="cell cell-updated">
              {incident.lastUpdated}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default IncidentsList