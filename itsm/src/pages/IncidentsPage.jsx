import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Breadcrumb from '../components/shared/Breadcrumb'
import FilterBar from '../components/incidents/FilterBar'
import IncidentsList from '../components/incidents/IncidentsList'
import Button from '../components/shared/Button'
import { useIncidents } from '../context/IncidentsContext'
import { FiPlus } from 'react-icons/fi'

function IncidentsPage() {
  const navigate = useNavigate()
  const { incidents } = useIncidents()
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('All statuses')

  const filteredIncidents = incidents.filter(inc => {
    const matchesSearch = !search ||
      inc.id.toLowerCase().includes(search.toLowerCase()) ||
      inc.description.toLowerCase().includes(search.toLowerCase()) ||
      inc.client.toLowerCase().includes(search.toLowerCase()) ||
      inc.assignment.toLowerCase().includes(search.toLowerCase())

    const matchesStatus = filterStatus === 'All statuses' || inc.status === filterStatus

    return matchesSearch && matchesStatus
  })

  return (
    <main className="main-content">
      <div className="page-header">
        <Breadcrumb>OPERATIONS / QUEUE</Breadcrumb>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="page-title">Incidents</h1>
            <p className="page-description">Track and manage operational incidents across your organization</p>
          </div>
          <Button
            variant="primary"
            onClick={() => navigate('/incident/new')}
            className="px-[20px] py-[10px]"
          >
            <FiPlus size={16} />
            Create Incident
          </Button>
        </div>
      </div>

      <FilterBar onSearchChange={setSearch} onFilterChange={setFilterStatus} />
      <IncidentsList incidents={filteredIncidents} />

      <div className="footer">
        <div className="footer-left">
          <span className="sync-status">Queue synced just now</span>
        </div>
        <div className="footer-right">
          <span className="filter-status">Showing {filteredIncidents.length} operational incidents</span>
        </div>
      </div>
    </main>
  )
}

export default IncidentsPage