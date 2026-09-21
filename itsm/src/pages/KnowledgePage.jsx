import Breadcrumb from '../components/shared/Breadcrumb'
import KnowledgeCard from '../components/knowledge/KnowledgeCard'
import { knowledgeSources } from '../data/knowledge'
import { useChat } from '../context/ChatContext'
import { FiStar } from 'react-icons/fi'

function KnowledgePage() {
  const { openChat } = useChat()

  return (
    <main className="main-content">
      <div className="page-header">
        <Breadcrumb>KNOWLEDGE / SOURCES</Breadcrumb>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="page-title">Knowledge Base</h1>
            <p className="page-description">Access client documentation, runbooks, and service level agreements</p>
          </div>
          <button 
            onClick={() => openChat({ 
              placeholder: 'Ask about knowledge base...',
              placeholderText: 'Ask about CODs, runbooks, or SLAs'
            })}
            className="sparkle-btn"
            title="Open AI Assistant"
          >
            <FiStar size={20} fill="#1c1c1c" color="#1c1c1c" />
          </button>
        </div>
      </div>

      <div className="knowledge-grid">
        {knowledgeSources.map((source) => (
          <KnowledgeCard key={source.id} source={source} />
        ))}
      </div>

      <div className="footer">
        <div className="footer-left">
          <span className="sync-status">Knowledge base synced just now</span>
        </div>
        <div className="footer-right">
          <span className="filter-status">3 knowledge sources available</span>
        </div>
      </div>
    </main>
  )
}

export default KnowledgePage