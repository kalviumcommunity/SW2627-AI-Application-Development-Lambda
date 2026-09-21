import { createContext, useContext, useState } from 'react'
import { incidents as initialIncidents } from '../data/incidents'
import { activities as initialActivities } from '../data/activities'

const IncidentsContext = createContext(null)

export function IncidentsProvider({ children }) {
  const [incidents, setIncidents] = useState(initialIncidents)
  const [activities, setActivities] = useState(initialActivities)

  const addIncident = (incidentData) => {
    // Generate next INC ID
    const currentMaxNum = incidents.reduce((max, inc) => {
      const match = inc.id.match(/^INC-(\d+)$/)
      if (match) {
        const num = parseInt(match[1], 10)
        return num > max ? num : max
      }
      return max
    }, 1042)

    const newId = `INC-${currentMaxNum + 1}`

    const newIncident = {
      id: newId,
      description: incidentData.description || 'New Incident',
      client: incidentData.client || 'Acme Financial Services',
      assignment: incidentData.assignment || 'Platform Support',
      status: incidentData.status || 'Investigating',
      lastUpdated: 'Just now',
      service: incidentData.service || 'Payment API',
      priority: incidentData.priority || 'P2 - High',
      details: incidentData.details || '',
    }

    const initialActivity = {
      id: Date.now(),
      author: 'Alex Rivera',
      initials: 'AR',
      time: 'Just now',
      message: incidentData.details 
        ? `Incident created: ${incidentData.details}`
        : `Incident ${newId} created and assigned to ${newIncident.assignment}.`,
    }

    setIncidents(prev => [newIncident, ...prev])
    setActivities(prev => ({
      ...prev,
      [newId]: [initialActivity]
    }))

    return newIncident
  }

  const addActivity = (incidentId, message, author = 'Alex Rivera', initials = 'AR') => {
    const newAct = {
      id: Date.now(),
      author,
      initials,
      time: 'Just now',
      message,
    }
    setActivities(prev => ({
      ...prev,
      [incidentId]: [...(prev[incidentId] || []), newAct]
    }))
  }

  const getIncident = (id) => {
    return incidents.find(inc => inc.id === id)
  }

  return (
    <IncidentsContext.Provider value={{ incidents, activities, addIncident, addActivity, getIncident }}>
      {children}
    </IncidentsContext.Provider>
  )
}

export function useIncidents() {
  const context = useContext(IncidentsContext)
  if (!context) {
    throw new Error('useIncidents must be used within an IncidentsProvider')
  }
  return context
}
