import { useRef, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../../context/ChatContext";
import { FiUser, FiCopy, FiCheck, FiDownload } from "react-icons/fi";
import { TbLambda } from "react-icons/tb";
import { pdf, Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import MarkdownIt from 'markdown-it';

const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 30,
  },
  title: {
    fontSize: 18,
    marginBottom: 15,
    color: '#1c1c1c',
  },
  content: {
    fontSize: 10,
    lineHeight: 1.5,
    color: '#1c1c1c',
  },
  h1: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1c1c1c',
  },
  h2: {
    fontSize: 15,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1c1c1c',
  },
  h3: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 6,
    color: '#1c1c1c',
  },
  bold: {
    fontWeight: 'bold',
  },
  italic: {
    fontStyle: 'italic',
  },
  code: {
    fontFamily: 'Courier',
    backgroundColor: '#f0f0f0',
    padding: 1,
    fontSize: 9,
  },
  codeBlock: {
    fontFamily: 'Courier',
    backgroundColor: '#f0f0f0',
    padding: 8,
    marginBottom: 8,
    fontSize: 9,
  },
  listItem: {
    marginLeft: 15,
    marginBottom: 3,
  },
  paragraph: {
    marginBottom: 6,
  },
});

function ChatContent({
  placeholderText = "Start a conversation to get assistance with this incident",
}) {
  const { messages, isLoadingContext, isBotLoading, error } = useChat();
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

  const parseMarkdownToPDF = (markdown) => {
    const md = new MarkdownIt();
    const tokens = md.parse(markdown);

    const renderToken = (token) => {
      switch (token.type) {
        case 'heading_open':
          const level = parseInt(token.tag.slice(1));
          return { type: 'heading_open', level };

        case 'heading_close':
          return { type: 'heading_close' };

        case 'paragraph_open':
          return { type: 'paragraph_open' };

        case 'paragraph_close':
          return { type: 'paragraph_close' };

        case 'inline':
          return token.children ? token.children.map(renderToken).flat() : [];

        case 'strong_open':
          return { type: 'strong_open' };

        case 'strong_close':
          return { type: 'strong_close' };

        case 'em_open':
          return { type: 'em_open' };

        case 'em_close':
          return { type: 'em_close' };

        case 'code_inline':
          return { type: 'code_inline', content: token.content };

        case 'code_block':
          return { type: 'code_block', content: token.content };

        case 'bullet_list_open':
          return { type: 'bullet_list_open' };

        case 'bullet_list_close':
          return { type: 'bullet_list_close' };

        case 'list_item_open':
          return { type: 'list_item_open' };

        case 'list_item_close':
          return { type: 'list_item_close' };

        case 'ordered_list_open':
          return { type: 'ordered_list_open' };

        case 'ordered_list_close':
          return { type: 'ordered_list_close' };

        case 'text':
          return { type: 'text', content: token.content };

        case 'softbreak':
          return { type: 'softbreak' };

        case 'hardbreak':
          return { type: 'hardbreak' };

        case 'link_open':
          return { type: 'link_open', href: token.attrGet('href') };

        case 'link_close':
          return { type: 'link_close' };

        default:
          return [];
      }
    };

    const elements = tokens.map(renderToken).flat();

    const renderElements = (elements) => {
      const result = [];
      let currentText = [];
      let inBold = false;
      let inItalic = false;
      let inCode = false;
      let inLink = false;
      let currentLink = null;
      let currentHeadingLevel = null;
      let inParagraph = false;
      let inList = false;
      let inListItem = false;
      let listType = null;
      let listItemNumber = 0;

      for (let i = 0; i < elements.length; i++) {
        const el = elements[i];

        switch (el.type) {
          case 'heading_open':
            currentHeadingLevel = el.level;
            break;

          case 'heading_close':
            if (currentText.length > 0) {
              const headingStyle = currentHeadingLevel === 1 ? styles.h1 :
                                  currentHeadingLevel === 2 ? styles.h2 : styles.h3;
              result.push(<Text key={`h-${i}`} style={headingStyle}>{currentText}</Text>);
              currentText = [];
            }
            currentHeadingLevel = null;
            break;

          case 'paragraph_open':
            inParagraph = true;
            break;

          case 'paragraph_close':
            if (currentText.length > 0) {
              result.push(<Text key={`p-${i}`} style={styles.paragraph}>{currentText}</Text>);
              currentText = [];
            }
            inParagraph = false;
            break;

          case 'bullet_list_open':
            inList = true;
            listType = 'bullet';
            break;

          case 'ordered_list_open':
            inList = true;
            listType = 'ordered';
            listItemNumber = 0;
            break;

          case 'bullet_list_close':
          case 'ordered_list_close':
            inList = false;
            listType = null;
            break;

          case 'list_item_open':
            inListItem = true;
            if (listType === 'ordered') {
              listItemNumber++;
            }
            break;

          case 'list_item_close':
            if (currentText.length > 0) {
              const prefix = listType === 'bullet' ? '• ' : `${listItemNumber}. `;
              result.push(
                <Text key={`li-${i}`} style={styles.listItem}>
                  {prefix}{currentText}
                </Text>
              );
              currentText = [];
            }
            inListItem = false;
            break;

          case 'strong_open':
            inBold = true;
            break;

          case 'strong_close':
            inBold = false;
            break;

          case 'em_open':
            inItalic = true;
            break;

          case 'em_close':
            inItalic = false;
            break;

          case 'code_inline':
            currentText.push(<Text key={`code-${i}`} style={styles.code}>{el.content}</Text>);
            break;

          case 'code_block':
            result.push(
              <Text key={`codeblock-${i}`} style={styles.codeBlock}>
                {el.content}
              </Text>
            );
            break;

          case 'link_open':
            inLink = true;
            currentLink = el.href;
            break;

          case 'link_close':
            inLink = false;
            currentLink = null;
            break;

          case 'text':
            let textElement = el.content;
            if (inBold) {
              textElement = <Text key={`text-${i}`} style={styles.bold}>{textElement}</Text>;
            }
            if (inItalic) {
              textElement = <Text key={`text-${i}`} style={styles.italic}>{textElement}</Text>;
            }
            if (inLink) {
              textElement = <Text key={`text-${i}`} style={{ color: '#0066cc', textDecoration: 'underline' }}>{textElement}</Text>;
            }
            currentText.push(textElement);
            break;

          case 'softbreak':
            currentText.push(' ');
            break;

          case 'hardbreak':
            currentText.push('\n');
            break;
        }
      }

      // Add any remaining text
      if (currentText.length > 0) {
        result.push(<Text key="final" style={styles.paragraph}>{currentText}</Text>);
      }

      return result;
    };

    return renderElements(elements);
  };

  const handleDownload = async (message, index) => {
    const rawContent = message.message;
    const pdfContent = parseMarkdownToPDF(rawContent);

    const MyDocument = () => (
      <Document>
        <Page size="A4" style={styles.page}>
          {pdfContent}
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
      {messages && messages.length === 0 && !isLoadingContext && !isBotLoading ? (
        <div className="flex flex-col items-center justify-center h-full text-center p-6">
          <div className="mb-4 p-4 rounded-full bg-[#1c1c1c]">
            <TbLambda className="w-8 h-8 text-white" />
          </div>

          <p className="text-base font-semibold text-[#1c1c1c] mb-1">
            AI Assistant ready to help
          </p>

          <p className="text-xs text-[#666] max-w-xs">{placeholderText}</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4 p-4">

          {isLoadingContext && messages.length === 0 && (
            <div className="flex items-start gap-2.5">
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-[#1c1c1c] text-white flex-shrink-0">
                <TbLambda className="w-3.5 h-3.5" />
              </div>

              <div className="bg-[#fafafa]/50 text-[#1c1c1c] rounded-xl rounded-tl-none py-2.5 px-3.5">
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
                      : "bg-[#1c1c1c] text-white"
                  }`}
                >
                  {isUser ? (
                    <FiUser className="w-3.5 h-3.5" />
                  ) : (
                    <TbLambda className="w-3.5 h-3.5" />
                  )}
                </div>

                <div
                  className={`group relative max-w-[75%] text-sm leading-relaxed ${
                    isUser
                      ? "bg-[#1c1c1c] text-white rounded-xl rounded-tr-none py-2.5 px-3.5"
                      : "bg-[#fafafa]/50 text-[#1c1c1c] rounded-xl rounded-tl-none py-0 px-0"
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
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-[#1c1c1c] text-white flex-shrink-0">
                <TbLambda className="w-3.5 h-3.5" />
              </div>

              <div className="bg-[#fafafa]/50 text-[#1c1c1c] rounded-xl rounded-tl-none py-2.5 px-3.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-[#666]">
                    {isLoadingContext ? "Loading context" : "Lambda is thinking..."}
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
