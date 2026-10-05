import { useState, useEffect } from "react";
import { FiPlus, FiX, FiTrash2, FiClock } from "react-icons/fi";
import { TbLambda } from "react-icons/tb";
import { useChat } from "../../context/ChatContext";

function ChatHeader({ onClose, showUser = false }) {
  const { chatContext, startNewThread, pruneLocalStorage } = useChat();

  const incidentContext = chatContext.incidentContext || {};
  const clientId = incidentContext.client_id;
  const rawPriority = incidentContext.priority || "";
  const priorityCode = rawPriority.split(" ")[0];

  const [contextData, setContextData] = useState({
    slas: [],
    special_instructions: [],
  });

  const [contextLoading, setContextLoading] = useState(false);

  useEffect(() => {
    if (!clientId) {
      setContextData({
        slas: [],
        special_instructions: [],
      });
      return;
    }

    const contextApiUrl = import.meta.env.VITE_CONTEXT_API_URL || "http://localhost:5001";
    const url = new URL(`${contextApiUrl}/api/context/client/${clientId}`);

    if (priorityCode) {
      url.searchParams.set("priority", priorityCode);
    }

    setContextLoading(true);

    fetch(url.toString())
      .then((r) =>
        r.ok ? r.json() : Promise.reject(new Error("Failed to load context")),
      )
      .then((data) => {
        setContextData({
          slas: Array.isArray(data.slas) ? data.slas : [],
          special_instructions: Array.isArray(data.special_instructions)
            ? data.special_instructions
            : [],
        });
      })
      .catch(() => {
        setContextData({
          slas: [],
          special_instructions: [],
        });
      })
      .finally(() => {
        setContextLoading(false);
      });
  }, [clientId, priorityCode]);

  const priorities = contextData.slas.flatMap(
    (sla) => sla.sla_priorities || [],
  );

  return (
    <div className="bg-white px-4 py-2.5 select-none">
      <div className="flex items-center justify-between gap-3">
        {/* Left Branding & Context Details */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-[#09090b] flex items-center justify-center flex-shrink-0 shadow-sm">
            <TbLambda className="w-4 h-4 text-white stroke-[2.5]" />
          </div>

          <div className="min-w-0 flex flex-col justify-center">
            <div className="flex items-center gap-1.5">
              <span className="text-[13px] font-bold text-[#09090b] tracking-tight">
                Lambda AI
              </span>
            </div>

            {incidentContext.id ? (
              <div className="text-[11px] font-medium text-[#52525b] truncate max-w-[180px] mt-0.5">
                {incidentContext.id} <span className="text-[#a1a1aa]">•</span> {incidentContext.client}
              </div>
            ) : (
              <div className="text-[11px] font-normal text-[#71717a] mt-0.5">
                Contextual Operations Agent
              </div>
            )}
          </div>
        </div>

        {/* Center Compact SLA Badge */}
        {clientId && (
          <div className="hidden sm:flex items-center flex-1 justify-center px-1">
            {contextLoading ? (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#f4f4f5] border border-[#e4e4e7] text-[10px] text-[#71717a]">
                <div className="w-2.5 h-2.5 border-2 border-[#a1a1aa] border-t-[#09090b] rounded-full animate-spin" />
                Loading SLAs...
              </div>
            ) : priorities.length > 0 ? (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#f4f4f5] border border-[#e4e4e7] text-[11px] text-[#27272a]">
                <FiClock className="w-3 h-3 text-[#71717a]" />
                {priorities.slice(0, 1).map((p, idx) => (
                  <div key={p.id || idx} className="flex items-center gap-1.5">
                    <span className="font-semibold text-[#09090b]">{p.priority_level}</span>
                    <span className="text-[#a1a1aa]">•</span>
                    {p.response_target_minutes && (
                      <span>Resp {p.response_target_minutes}m</span>
                    )}
                    {p.restore_target_hours && (
                      <span>Res {p.restore_target_hours}h</span>
                    )}
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        )}

        {/* Right Action Buttons */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            onClick={startNewThread}
            className="w-8 h-8 flex items-center justify-center rounded-md border border-[#e4e4e7] bg-white text-[#27272a] hover:bg-[#09090b] hover:text-white hover:border-[#09090b] transition-all shadow-2xs group"
            title="Start new conversation thread"
          >
            <FiPlus className="w-4 h-4 transition-transform group-hover:rotate-90 duration-200" />
          </button>

          <button
            onClick={pruneLocalStorage}
            className="w-8 h-8 flex items-center justify-center rounded-md border border-[#e4e4e7] bg-white text-[#27272a] hover:bg-[#09090b] hover:text-white hover:border-[#09090b] transition-all shadow-2xs"
            title="Clear stored thread cache"
          >
            <FiTrash2 className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-[#e4e4e7] mx-0.5" />

          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-md border border-[#e4e4e7] bg-white text-[#27272a] hover:bg-[#09090b] hover:text-white hover:border-[#09090b] transition-all shadow-2xs"
            aria-label="Close chat (Esc)"
            title="Close sidebar (Esc)"
          >
            <FiX className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatHeader;
