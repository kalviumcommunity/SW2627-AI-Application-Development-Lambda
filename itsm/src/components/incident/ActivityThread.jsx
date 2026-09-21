import Avatar from '../shared/Avatar'

function ActivityThread({ activities }) {
  return (
    <div className="activity-section">
      <div className="activity-header-row">
        <h2 className="section-title">Activity</h2>
        <button className="add-update-btn">Add update</button>
      </div>
      <div className="activity-thread">
        {activities.map((activity) => (
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