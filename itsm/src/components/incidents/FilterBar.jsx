import { useState } from 'react'
import Input from '../shared/Input'

function FilterBar({ onSearchChange, onFilterChange }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('All statuses')

  const handleSearchChange = (e) => {
    const value = e.target.value
    setSearchTerm(value)
    onSearchChange?.(value)
  }

  const handleFilterChange = (e) => {
    const value = e.target.value
    setStatusFilter(value)
    onFilterChange?.(value)
  }

  return (
    <div className="filter-bar">
      <Input
        type="text"
        placeholder="Search incidents..."
        icon={true}
        value={searchTerm}
        onChange={handleSearchChange}
      />
      <div className="filter-wrapper">
        <select
          value={statusFilter}
          onChange={handleFilterChange}
          className="status-filter"
        >
          <option>All statuses</option>
          <option>Open</option>
          <option>In Progress</option>
          <option>Resolved</option>
        </select>
      </div>
    </div>
  )
}

export default FilterBar