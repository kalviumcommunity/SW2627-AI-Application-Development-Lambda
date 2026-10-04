import { useState } from 'react'
import Avatar from '../shared/Avatar'

function ActivityThread({ activities, onAddUpdate }) {
  const [isAdding, setIsAdding] = useState(false)
  const [updateText, setUpdateText] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!updateText.trim()) return
    if (onAddUpdate) {
      onAddUpdate(updateText.trim())
    }
    setUpdateText('')
    setIsAdding(false)
  }

  return (
    <div className="activity-section">
      <div className="activity-header-row">
        <h2 className="section-title">Activity</h2>
        {!isAdding && (
          <button 
            className="add-update-btn"
            onClick={() => setIsAdding(true)}
          >
            Add update
          </button>
        )}
      </div>

      {isAdding && (
        <form onSubmit={handleSubmit} className="add-update-form mb-6 p-4 bg-[#fafafa] border border-[#e8e8e8] rounded-lg flex flex-col gap-3">
          <textarea
            value={updateText}
            onChange={(e) => setUpdateText(e.target.value)}
            placeholder="Write an update for this incident..."
            rows={2}
            autoFocus
            className="w-full p-3 text-sm text-[#1c1c1c] bg-white border border-[#e8e8e8] rounded-md outline-none focus:border-[#1c1c1c] transition-colors resize-none"
          />
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => {
                setIsAdding(false)
                setUpdateText('')
              }}
              className="px-3 py-1.5 text-xs font-medium text-[#666] hover:text-[#1c1c1c] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!updateText.trim()}
              className="px-4 py-1.5 text-xs font-medium text-white bg-[#1c1c1c] rounded-md hover:bg-[#333] disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              Post update
            </button>
          </div>
        </form>
      )}

      <div className="activity-thread">
        {[...activities].reverse().map((activity) => (
          <div key={activity.id} className="activity-item">
            <Avatar initials={activity.initials} size="activity" />
            <div className="activity-content">
              <div className="activity-header">
                <span className="activity-author">{activity.author}</span>
                <span className="activity-time">{activity.time}</span>
              </div>
              <div className="activity-message">{activity.message}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ActivityThread