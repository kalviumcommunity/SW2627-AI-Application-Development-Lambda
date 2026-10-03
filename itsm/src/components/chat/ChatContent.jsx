import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../../context/ChatContext";
import { FiUser, FiCopy, FiCheck } from "react-icons/fi";
import { TbLambda } from "react-icons/tb";

function ChatContent({
  placeholderText = "Start a conversation to get assistance with this incident",
}) {
  const { messages, isLoadingContext, isBotLoading } = useChat();
  const messagesEndRef = useRef(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotLoading]);

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);

    setTimeout(() => {
      setCopiedIndex(null);
    }, 2000);
  };

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {isLoadingContext && messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center p-6">
          <div className="mb-4 p-4 rounded-full bg-[#fafafa] border border-[#e8e8e8]">
            <TbLambda className="w-8 h-8 text-[#1c1c1c]" />
          </div>

          <div className="flex items-center gap-2 rounded-full border border-[#e8e8e8] bg-[#f5f5f5] px-3 py-2">
            <span className="text-xs font-medium text-[#666]">
              Loading context
            </span>
            <div className="flex items-center gap-1.5">
              <span className="dot-loader dot-1" />
              <span className="dot-loader dot-2" />
              <span className="dot-loader dot-3" />
            </div>
          </div>
        </div>
      ) : messages && messages.length === 0 && !isLoadingContext ? (
        <div className="flex flex-col items-center justify-center h-full text-center p-6">
          <div className="mb-4 p-4 rounded-full bg-[#fafafa] border border-[#e8e8e8]">
            <TbLambda className="w-8 h-8 text-[#1c1c1c]" />
          </div>

          <p className="text-base font-semibold text-[#1c1c1c] mb-1">
            AI Assistant ready to help
          </p>

          <p className="text-xs text-[#666] max-w-xs">{placeholderText}</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4 p-4">
          {messages.map((message, index) => {
            const isUser = message.role === "user";
            const isBot = message.role === "bot";

            const resourceList = Array.isArray(message.resources)
              ? message.resources.slice(0, 3)
              : [];

            return (
              <div
                key={index}
                className={`flex items-start gap-2.5 ${
                  isUser ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs flex-shrink-0 font-medium ${
                    isUser
                      ? "bg-[#1c1c1c] text-white"
                      : "bg-[#f5f5f5] border border-[#e8e8e8] text-[#1c1c1c]"
                  }`}
                >
                  {isUser ? (
                    <FiUser className="w-3.5 h-3.5" />
                  ) : (
                    <TbLambda className="w-3.5 h-3.5" />
                  )}
                </div>

                <div
                  className={`group relative max-w-[90%] py-2.5 px-3.5 rounded-xl text-sm leading-relaxed overflow-x-auto ${
                    isUser
                      ? "bg-[#1c1c1c] text-white rounded-tr-none"
                      : "bg-[#f5f5f5] text-[#1c1c1c] border border-[#e8e8e8] rounded-tl-none"
                  }`}
                >
                  <div className="markdown-body">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table({ children }) {
                          return (
                            <div className="my-2 overflow-x-auto rounded border border-[#e8e8e8]">
                              <table
                                className={`w-full text-left text-xs border-collapse ${
                                  isUser ? "text-white" : "text-[#1c1c1c]"
                                }`}
                              >
                                {children}
                              </table>
                            </div>
                          );
                        },

                        thead({ children }) {
                          return (
                            <thead
                              className={`${
                                isUser ? "bg-white/10" : "bg-[#fafafa]"
                              } border-b border-[#e8e8e8]`}
                            >
                              {children}
                            </thead>
                          );
                        },

                        th({ children }) {
                          return (
                            <th className="p-2 font-semibold border-r last:border-r-0 border-[#e8e8e8]">
                              {children}
                            </th>
                          );
                        },

                        td({ children }) {
                          return (
                            <td className="p-2 border-t border-r last:border-r-0 border-[#e8e8e8]">
                              {children}
                            </td>
                          );
                        },

                        code({ inline, className, children, ...props }) {
                          return inline ? (
                            <code
                              className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                                isUser
                                  ? "bg-white/20 text-white"
                                  : "bg-slate-200 text-slate-800"
                              }`}
                              {...props}
                            >
                              {children}
                            </code>
                          ) : (
                            <pre
                              className={`p-3 my-2 rounded-lg text-xs font-mono overflow-x-auto ${
                                isUser
                                  ? "bg-black/40 text-gray-100"
                                  : "bg-[#1c1c1c] text-slate-100"
                              }`}
                            >
                              <code {...props}>{children}</code>
                            </pre>
                          );
                        },

                        a({ href, children, ...props }) {
                          return (
                            <a
                              href={href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={`underline ${
                                isUser
                                  ? "text-white font-medium"
                                  : "text-slate-900 font-medium hover:text-black"
                              }`}
                              {...props}
                            >
                              {children}
                            </a>
                          );
                        },

                        ul({ children }) {
                          return (
                            <ul className="list-disc ml-4 space-y-1 my-1">
                              {children}
                            </ul>
                          );
                        },

                        ol({ children }) {
                          return (
                            <ol className="list-decimal ml-4 space-y-1 my-1">
                              {children}
                            </ol>
                          );
                        },

                        p({ children }) {
                          return (
                            <p className="my-0.5 whitespace-pre-wrap">
                              {children}
                            </p>
                          );
                        },
                      }}
                    >
                      {message.message}
                    </ReactMarkdown>
                  </div>

                  {isBot && resourceList.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-2">
                      {resourceList.map((resource, resourceIndex) => {
                        const shortenedTitle =
                          resource.title && resource.title.length > 18
                            ? `${resource.title.slice(0, 18)}...`
                            : resource.title || "Resource";

                        const shortenedId =
                          resource.id && resource.id.length > 18
                            ? `${resource.id.slice(0, 18)}...`
                            : resource.id || "N/A";

                        const popupTitle =
                          resource.title && resource.title.length > 32
                            ? `${resource.title.slice(0, 32)}...`
                            : resource.title || "Resource";

                        return (
                          <div
                            key={`${resource.id || resourceIndex}-resource`}
                            className="relative"
                          >
                            {/* Resource button */}
                            <button
                              type="button"
                              className="peer px-2.5 py-1.5 rounded-full border border-[#d8d8d8] bg-white/80 text-[11px] font-medium text-[#1c1c1c] shadow-sm transition-colors hover:bg-white"
                            >
                              {shortenedTitle}
                            </button>

                            {/* Popup belongs only to this resource */}
                            <div
                              className="
                                pointer-events-none
                                absolute
                                bottom-full
                                left-1/2
                                z-50
                                mb-2
                                w-56
                                -translate-x-1/2
                                rounded-lg
                                border
                                border-[#e8e8e8]
                                bg-white
                                p-2.5
                                text-left
                                shadow-lg
                                opacity-0
                                invisible
                                transition-all
                                duration-150
                                peer-hover:opacity-100
                                peer-hover:visible
                              "
                            >
                              <div className="mb-1 border-b border-[#f0f0f0] pb-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-[#666]">
                                Resource
                              </div>

                              <div className="space-y-1 text-[10px] text-[#1c1c1c]">
                                <div className="flex items-start gap-2">
                                  <span className="min-w-[2.5rem] font-medium text-[#666]">
                                    id:
                                  </span>

                                  <span
                                    className="break-all"
                                    title={resource.id || "N/A"}
                                  >
                                    {shortenedId}
                                  </span>
                                </div>

                                <div className="flex items-start gap-2">
                                  <span className="min-w-[2.5rem] font-medium text-[#666]">
                                    title:
                                  </span>

                                  <span
                                    className="break-words"
                                    title={resource.title || "N/A"}
                                  >
                                    {popupTitle}
                                  </span>
                                </div>

                                <div className="flex items-start gap-2">
                                  <span className="min-w-[2.5rem] font-medium text-[#666]">
                                    type:
                                  </span>

                                  <span
                                    className="break-all"
                                    title={resource.type || "N/A"}
                                  >
                                    {resource.type || "N/A"}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <button
                    onClick={() => handleCopy(message.message, index)}
                    className={`absolute top-2 ${
                      isUser
                        ? "-left-7 text-gray-400 hover:text-white"
                        : "-right-7 text-[#666] hover:text-[#1c1c1c]"
                    } opacity-0 group-hover:opacity-100 transition-opacity p-1`}
                    title="Copy message"
                    aria-label="Copy message"
                  >
                    {copiedIndex === index ? (
                      <FiCheck className="w-3.5 h-3.5 text-emerald-600" />
                    ) : (
                      <FiCopy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>
            );
          })}

          {isBotLoading && (
            <div className="flex items-start gap-2.5">
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-[#f5f5f5] border border-[#e8e8e8] text-[#1c1c1c] flex-shrink-0">
                <TbLambda className="w-3.5 h-3.5" />
              </div>

              <div className="bg-[#f5f5f5] text-[#1c1c1c] border border-[#e8e8e8] rounded-xl rounded-tl-none py-2.5 px-3.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-[#666]">
                    Loading context
                  </span>

                  <div className="flex items-center gap-1.5">
                    <span className="dot-loader dot-1" />
                    <span className="dot-loader dot-2" />
                    <span className="dot-loader dot-3" />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
}

export default ChatContent;
