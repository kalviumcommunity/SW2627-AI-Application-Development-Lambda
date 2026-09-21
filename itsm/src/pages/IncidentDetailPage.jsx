import { useParams } from 'react-router-dom'
import BackNav from '../components/shared/BackNav'
import IncidentHeader from '../components/incident/IncidentHeader'
import KeyInfo from '../components/incident/KeyInfo'
import Description from '../components/incident/Description'
import ActivityThread from '../components/incident/ActivityThread'
import { useIncidents } from '../context/IncidentsContext'
import { useChat } from '../context/ChatContext'

function IncidentDetailPage() {
  const { id } = useParams()
  const { incidents, activities } = useIncidents()
  const { openChat } = useChat()

  const incident = incidents.find(inc => inc.id === id)
  const incidentActivities = activities[id] || []

  if (!incident) {
    return (
      <main className="main-content incident-detail">
        <BackNav to="/" text="Back to incidents" />
        <h1 className="page-title">Incident not found</h1>
        <p className="page-description">The requested incident ID ({id}) could not be located in the system queue.</p>
      </main>
    )
  }

  const handleSparkleClick = () => {
    openChat({
      showContext: true,
      showSuggestions: true,
      showUser: true,
      placeholder: `Ask about ${incident.id}...`,
      placeholderText: `Start a conversation to get assistance with ${incident.id}`,
    })
  }

  const descriptionText = incident.details ||
    `${incident.service} is experiencing issues affecting ${incident.client}. Assignment: ${incident.assignment}.`

  return (
    <main className="main-content incident-detail">
      <BackNav to="/" text="Back to incidents" />
      <IncidentHeader incident={incident} onSparkleClick={handleSparkleClick} />
      <KeyInfo incident={incident} />
      <Description text={descriptionText} />
      <ActivityThread activities={incidentActivities} />
    </main>
  )
}

export default IncidentDetailPage