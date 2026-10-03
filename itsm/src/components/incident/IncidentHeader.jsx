import { HiSparkles } from "react-icons/hi2";

function IncidentHeader({ incident, onSparkleClick }) {
  return (
    <div className="incident-header">
      <div className="incident-id-row">
        <div>
          <button
            onClick={onSparkleClick}
            className="sparkle-btn border border-slate-900"
            title="LambdaAssist"
          >
            {" "}
            <HiSparkles className="w-[18px] h-[18px] text-[#1c1c1c]" />
          </button>
          <div className="incident-id">{incident.id}</div>
        </div>
      </div>
      <h1 className="incident-title">{incident.description}</h1>
      <div className="incident-status">
        <span className="status-dot"></span>
        <span className="status-text">{incident.status}</span>
      </div>
    </div>
  );
}

export default IncidentHeader;
