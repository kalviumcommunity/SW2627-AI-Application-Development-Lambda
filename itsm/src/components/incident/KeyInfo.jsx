function KeyInfo({ incident }) {
  return (
    <div className="key-info">
      <div className="info-card">
        <div className="info-label">Client</div>
        <div className="info-value">{incident.client}</div>
      </div>
      <div className="info-card">
        <div className="info-label">Assignment</div>
        <div className="info-value">{incident.assignment}</div>
      </div>
      <div className="info-card">
        <div className="info-label">Service</div>
        <div className="info-value">{incident.service || 'Payment API'}</div>
      </div>
      <div className="info-card">
        <div className="info-label">Priority</div>
        <div className="info-value">{incident.priority || 'P1 - Critical'}</div>
      </div>
    </div>
  )
}

export default KeyInfo