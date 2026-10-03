import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../../context/ChatContext";
import { FiUser, FiCopy, FiCheck, FiDownload } from "react-icons/fi";
import { TbLambda } from "react-icons/tb";
import { pdf, Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 40,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
    color: '#1c1c1c',
  },
  content: {
    fontSize: 12,
    lineHeight: 1.6,
    color: '#1c1c1c',
  },
});

function ChatContent({
  placeholderText = "Start a conversation to get assistance with this incident",
}) {
  const { messages, isLoadingContext, isBotLoading } = useChat();
  const messagesEndRef = useRef(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [expandedResources, setExpandedResources] = useState({});

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

  const handleDownload = async (message, index) => {
    const content = message.message;

    const MyDocument = () => (
      <Document>
        <Page size="A4" style={styles.page}>
          <Text style={styles.content}>{content}</Text>
        </Page>
      </Document>
    );

    try {
      const blob = await pdf(<MyDocument />).toBlob();
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF');
    }
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
              ? message.resources
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
                  className={`group relative max-w-[75%] py-2.5 px-3.5 rounded-xl text-sm leading-relaxed ${
                    isUser
                      ? "bg-[#1c1c1c] text-white rounded-tr-none"
                      : "bg-[#f5f5f5] text-[#1c1c1c] border border-[#e8e8e8] rounded-tl-none"
                  }`}
                >
                  <div className="markdown-body overflow-hidden break-words">
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
                    <div className="mt-2.5">
                      <button
                        type="button"
                        onClick={() => setExpandedResources(prev => ({
                          ...prev,
                          [index]: !prev[index]
                        }))}
                        className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-[#666] hover:text-[#1c1c1c] transition-colors"
                      >
                        <span>Sources</span>
                        <span className="px-1.5 py-0.5 rounded-full bg-[#e8e8e8] text-[10px] font-medium text-[#1c1c1c]">
                          {resourceList.length}
                        </span>
                        <svg
                          className={`w-3 h-3 transition-transform ${expandedResources[index] ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      </button>

                      {expandedResources[index] && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {resourceList.map((resource, resourceIndex) => {
                            const resourceName = resource.name || "Resource";
                            const shortenedName =
                              resourceName.length > 18
                                ? `${resourceName.slice(0, 18)}...`
                                : resourceName;

                            const resourceLink = resource.resource_link || "#";

                            return (
                              <a
                                key={resourceIndex}
                                href={resourceLink}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-block px-2.5 py-1.5 rounded-full border border-[#d8d8d8] bg-white/80 text-[11px] font-medium text-[#1c1c1c] shadow-sm transition-colors hover:bg-white hover:border-[#1c1c1c]"
                                title={resourceName}
                              >
                                {shortenedName}
                              </a>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  <div
                    className={`absolute top-2 flex flex-col gap-1 ${
                      isUser
                        ? "-left-9"
                        : "-right-9"
                    } opacity-0 group-hover:opacity-100 transition-opacity`}
                  >
                    <button
                      onClick={() => handleCopy(message.message, index)}
                      className={`p-1 ${
                        isUser
                          ? "text-gray-400 hover:text-white"
                          : "text-[#666] hover:text-[#1c1c1c]"
                      }`}
                      title="Copy message"
                      aria-label="Copy message"
                    >
                      {copiedIndex === index ? (
                        <FiCheck className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <FiCopy className="w-3.5 h-3.5" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDownload(message, index)}
                      className={`p-1 ${
                        isUser
                          ? "text-gray-400 hover:text-white"
                          : "text-[#666] hover:text-[#1c1c1c]"
                      }`}
                      title="Download as file"
                      aria-label="Download as file"
                    >
                      <FiDownload className="w-3.5 h-3.5" />
                    </button>
                  </div>
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
