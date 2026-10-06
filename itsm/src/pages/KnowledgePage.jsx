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
        </div>
      </div>

      <div className="knowledge-grid">
        {knowledgeSources.map((source) => (
          <KnowledgeCard key={source.id} source={source}/>
        ))}
      </div>
    </main>
  )
}

export default KnowledgePage