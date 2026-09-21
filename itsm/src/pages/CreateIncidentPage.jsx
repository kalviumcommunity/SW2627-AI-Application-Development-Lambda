import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Breadcrumb from '../components/shared/Breadcrumb'
import BackNav from '../components/shared/BackNav'
import { useIncidents } from '../context/IncidentsContext'

function CreateIncidentPage() {
  const navigate = useNavigate()
  const { addIncident } = useIncidents()

  const [formData, setFormData] = useState({
    description: '',
    client: 'Acme Financial Services',
    service: 'Payment API',
    priority: 'P1 - Critical',
    assignment: 'Platform Support',
    status: 'Investigating',
    details: '',
  })

  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (error) setError('')
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.description.trim()) {
      setError('Please provide a summary / title for the incident.')
      return
    }

    const created = addIncident(formData)
    navigate(`/incident/${created.id}`)
  }

  return (
    <main className="main-content incident-detail">
      <BackNav to="/" text="Back to incidents" />

      <div className="page-header">
        <Breadcrumb>OPERATIONS / CREATE INCIDENT</Breadcrumb>
        <h1 className="page-title">Create New Incident</h1>
        <p className="page-description">Report and log a new operational incident across your organization</p>
      </div>

      <form onSubmit={handleSubmit} className="border border-[#e8e8e8] rounded-[8px] bg-white p-[24px] mb-[32px]">
        {error && (
          <div className="mb-[20px] p-[12px] bg-[#fef2f2] border border-[#fecaca] rounded-[6px] text-[13px] text-[#dc2626]">
            {error}
          </div>
        )}

        <div className="flex flex-col gap-[20px]">
          {/* Incident Summary */}
          <div className="flex flex-col gap-[6px]">
            <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
              Incident Summary <span className="text-[#dc2626]">*</span>
            </label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="e.g. Payment API returning 502 Bad Gateway responses"
              className="w-full px-[14px] py-[10px] border border-[#e8e8e8] rounded-[6px] text-[14px] text-[#1c1c1c] bg-white outline-none transition-all duration-[150ms] ease focus:border-[#1c1c1c] focus:shadow-[0_0_0_3px_rgba(28,28,28,0.1)] placeholder:text-[#999]"
            />
          </div>

          {/* Row 1: Client & Service */}
          <div className="grid grid-cols-2 gap-[16px] grid-responsive">
            <div className="flex flex-col gap-[6px]">
              <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
                Affected Client
              </label>
              <select
                name="client"
                value={formData.client}
                onChange={handleChange}
                className="status-filter w-full"
              >
                <option value="Acme Financial Services">Acme Financial Services</option>
                <option value="Northstar Health Systems">Northstar Health Systems</option>
                <option value="VertexPay Financial">VertexPay Financial</option>
                <option value="TechCorp Industries">TechCorp Industries</option>
                <option value="BluePeak Retail Group">BluePeak Retail Group</option>
                <option value="Atlas Legal Partners">Atlas Legal Partners</option>
                <option value="GreenGrid Energy">GreenGrid Energy</option>
                <option value="Crestline Logistics">Crestline Logistics</option>
                <option value="Nimbus Media Studios">Nimbus Media Studios</option>
                <option value="StartupXYZ">StartupXYZ</option>
                <option value="Global Logistics">Global Logistics</option>
                <option value="MediaStream Inc">MediaStream Inc</option>
                <option value="FinTech Pro">FinTech Pro</option>
              </select>
            </div>

            <div className="flex flex-col gap-[6px]">
              <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
                Affected Service
              </label>
              <select
                name="service"
                value={formData.service}
                onChange={handleChange}
                className="status-filter w-full"
              >
                <option value="Payment API">Payment API</option>
                <option value="Database Service">Database Service</option>
                <option value="Auth Service">Auth Service</option>
                <option value="Email Service">Email Service</option>
                <option value="File Service">File Service</option>
                <option value="API Gateway">API Gateway</option>
                <option value="Infrastructure">Infrastructure</option>
              </select>
            </div>
          </div>

          {/* Row 2: Priority & Assignment */}
          <div className="grid grid-cols-3 gap-[16px] grid-responsive">
            <div className="flex flex-col gap-[6px]">
              <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
                Priority Level
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="status-filter w-full"
              >
                <option value="P1 - Critical">P1 - Critical</option>
                <option value="P2 - High">P2 - High</option>
                <option value="P3 - Medium">P3 - Medium</option>
                <option value="P4 - Low">P4 - Low</option>
              </select>
            </div>

            <div className="flex flex-col gap-[6px]">
              <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
                Assignment Group
              </label>
              <select
                name="assignment"
                value={formData.assignment}
                onChange={handleChange}
                className="status-filter w-full"
              >
                <option value="Platform Support">Platform Support</option>
                <option value="Database Team">Database Team</option>
                <option value="Security Team">Security Team</option>
                <option value="Messaging Team">Messaging Team</option>
                <option value="API Team">API Team</option>
                <option value="Infrastructure Team">Infrastructure Team</option>
              </select>
            </div>

            <div className="flex flex-col gap-[6px]">
              <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
                Initial Status
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="status-filter w-full"
              >
                <option value="Investigating">Investigating</option>
                <option value="In Progress">In Progress</option>
                <option value="Open">Open</option>
              </select>
            </div>
          </div>

          {/* Detailed Investigation Notes */}
          <div className="flex flex-col gap-[6px]">
            <label className="text-[12px] font-semibold text-[#666] uppercase tracking-[0.5px]">
              Initial Investigation Details & Description
            </label>
            <textarea
              name="details"
              rows={4}
              value={formData.details}
              onChange={handleChange}
              placeholder="Provide background context, application logs, error codes, or observed impacts..."
              className="w-full px-[14px] py-[10px] border border-[#e8e8e8] rounded-[6px] text-[14px] text-[#1c1c1c] bg-white outline-none transition-all duration-[150ms] ease focus:border-[#1c1c1c] focus:shadow-[0_0_0_3px_rgba(28,28,28,0.1)] placeholder:text-[#999]"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-[12px] pt-[8px] border-t border-[#e8e8e8]">
            <button
              type="submit"
              className="px-[20px] py-[10px] bg-[#1c1c1c] text-white text-[14px] font-medium rounded-[6px] cursor-pointer hover:bg-[#333] transition-all duration-[150ms] ease border-none"
            >
              Create Incident
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-[20px] py-[10px] bg-white text-[#1c1c1c] border border-[#e8e8e8] text-[14px] font-medium rounded-[6px] cursor-pointer hover:bg-[#f5f5f5] hover:border-[#1c1c1c] transition-all duration-[150ms] ease"
            >
              Cancel
            </button>
          </div>
        </div>
      </form>
    </main>
  )
}

export default CreateIncidentPage
