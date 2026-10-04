import { useState, useEffect } from "react";
import { FiPlus, FiX, FiTrash } from "react-icons/fi";
import { TbLambda } from "react-icons/tb";
import Avatar from "../shared/Avatar";
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

    const url = new URL(`http://localhost:5001/api/context/client/${clientId}`);

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
    <div>
      <div className="flex items-center gap-3 px-4 py-2.5">
        <div className="w-7 h-7 rounded bg-[#1c1c1c] flex items-center justify-center flex-shrink-0">
          <TbLambda className="w-4 h-4 text-white" />
        </div>

        <div className="min-w-0 flex-shrink-0">
          <div className="text-[13px] font-semibold text-[#1c1c1c] leading-tight">
            Lambda
          </div>

          {incidentContext.id ? (
            <div className="text-[11px] text-[#666] leading-tight truncate max-w-[180px]">
              {incidentContext.id} · {incidentContext.client}
            </div>
          ) : (
            <div className="text-[11px] text-[#999] leading-tight">
              Contextual support assistant
            </div>
          )}
        </div>

        {clientId && (
          <div className="flex-1 min-w-0 flex items-center">
            {contextLoading ? (
              <div className="flex items-center gap-1.5 text-[10px] text-[#999]">
                <div className="w-3 h-3 border-2 border-[#ddd] border-t-[#333] rounded-full animate-spin" />
                Loading SLAs...
              </div>
            ) : priorities.length > 0 ? (
              <div className="flex items-center gap-4 ml-5">
                {priorities.map((p, idx) => (
                  <div key={p.id || idx}>
                    <div>
                      <span className="text-[14px] font-bold text-[#1c1c1c]">
                        {p.priority_level} | {p.priority_name}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] text-[#888]">
                      {p.response_target_minutes && (
                        <span>
                          Resp{" "}
                          <span className="font-medium text-[#444]">
                            {p.response_target_minutes}m
                          </span>
                        </span>
                      )}

                      {p.restore_target_hours && (
                        <span>
                          Res{" "}
                          <span className="font-medium text-[#444]">
                            {p.restore_target_hours}h
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        )}

        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            onClick={startNewThread}
            className="w-7 h-7 flex items-center justify-center rounded bg-[#f0f0f0] hover:bg-[#e8e8e8] transition-colors"
            title="Start new thread"
          >
            <FiPlus className="w-3.5 h-3.5 text-[#1c1c1c]" />
          </button>
          <button
            onClick={pruneLocalStorage}
            className="w-7 h-7 flex items-center justify-center rounded bg-[#f0f0f0] hover:bg-[#e8e8e8] transition-colors"
            title="Prune local storage"
          >
            <FiTrash className="w-3.5 h-3.5 text-[#1c1c1c]" />
          </button>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded bg-[#f0f0f0] hover:bg-[#e8e8e8] transition-colors"
            aria-label="Close chat (Esc)"
            title="Close (Esc)"
          >
            <FiX className="w-3.5 h-3.5 text-[#1c1c1c]" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatHeader;
