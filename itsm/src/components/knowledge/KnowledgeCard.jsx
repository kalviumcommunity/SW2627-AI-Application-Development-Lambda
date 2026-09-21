import Badge from '../shared/Badge'

function KnowledgeCard({ source }) {
  const getIcon = (iconType) => {
    switch (iconType) {
      case 'document':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M14 2V8H20" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M16 13H8" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round"/>
            <path d="M16 17H8" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        )
      case 'layers':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )
      case 'clock':
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 6V12L16 14" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )
      default:
        return null
    }
  }

  return (
    <div className="knowledge-card">
      <div className="card-header">
        <div className="card-icon">
          {getIcon(source.icon)}
        </div>
        <div className="card-title-group">
          <h3 className="card-title">{source.title}</h3>
          <span className="card-subtitle">{source.subtitle}</span>
        </div>
        <Badge variant="source">{source.source}</Badge>
      </div>
      <div className="card-content">
        <p className="card-description">{source.description}</p>
        <div className="card-details">
          <div className="detail-item">
            <span className="detail-label">{source.details.label}</span>
            <span className="detail-value">{source.details.value}</span>
          </div>
        </div>
      </div>
      <div className="card-footer">
        <button className="card-action-btn">{source.action}</button>
      </div>
    </div>
  )
}

export default KnowledgeCard