import { useState } from 'react'

function ContextSection() {
  const [mainCollapsed, setMainCollapsed] = useState(false)
  const [incidentCollapsed, setIncidentCollapsed] = useState(false)
  const [clientCollapsed, setClientCollapsed] = useState(false)

  return (
    <div className="unified-context">
      <div 
        className={`context-header ${mainCollapsed ? 'collapsed' : ''}`}
        onClick={() => setMainCollapsed(!mainCollapsed)}
      >
        <span className="context-title">CONTEXT</span>
        <div className="context-header-right">
          <span className="grounded-tag">Grounded</span>
          <svg className="main-context-chevron" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
      
      <div className={`context-content ${mainCollapsed ? 'collapsed' : ''}`}>
        <div className="context-section">
          <div 
            className={`context-section-header ${incidentCollapsed ? 'collapsed' : ''}`}
            onClick={() => setIncidentCollapsed(!incidentCollapsed)}
          >
            <span className="context-section-title">Incident Details</span>
            <svg className="context-chevron" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 10L8 6L12 10" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className={`context-section-body ${incidentCollapsed ? 'collapsed' : ''}`}>
            <div className="context-item">
              <span className="context-id">INC-1042</span>
              <span className="context-client">Acme Financial Services</span>
            </div>
            <div className="context-item">
              <span className="context-service">Payment API</span>
              <span className="context-priority">P1 - Critical</span>
            </div>
            <div className="context-note">Production failover requires service-owner approval.</div>
          </div>
        </div>

        <div className="context-divider"></div>

        <div className="context-section">
          <div 
            className={`context-section-header ${clientCollapsed ? 'collapsed' : ''}`}
            onClick={() => setClientCollapsed(!clientCollapsed)}
          >
            <span className="context-section-title">Client Context</span>
            <svg className="context-chevron" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 10L8 6L12 10" stroke="#1c1c1c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className={`context-section-body ${clientCollapsed ? 'collapsed' : ''}`}>
            <div className="context-item">
              <span className="context-label">SLA:</span>
              <span className="context-value">15 minute response time for P1 incidents</span>
            </div>
            <div className="context-item">
              <span className="context-label">Contacts:</span>
              <span className="context-value">John Smith (Client Lead) - john.smith@acme.com</span>
            </div>
            <div className="context-item">
              <span className="context-label">Procedure:</span>
              <span className="context-value">Follow Payment API Production Runbook v2.3</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContextSection