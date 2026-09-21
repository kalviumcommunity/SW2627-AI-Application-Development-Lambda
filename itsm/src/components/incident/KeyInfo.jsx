function KeyInfo({ incident }) {
  return (
    <div className="key-info">
      <div className="info-item">
        <div className="info-label">CLIENT</div>
        <div className="info-value">{incident.client}</div>
      </div>
      <div className="info-item">
        <div className="info-label">ASSIGNMENT</div>
        <div className="info-value">{incident.assignment}</div>
      </div>
      <div className="info-item">
        <div className="info-label">SERVICE</div>
        <div className="info-value">{incident.service || 'Payment API'}</div>
      </div>
      <div className="info-item">
        <div className="info-label">PRIORITY</div>
        <div className="info-value">{incident.priority || 'P1 - Critical'}</div>
      </div>
    </div>
  )
}

export default KeyInfo