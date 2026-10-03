import { createContext, useContext, useState } from "react";

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatContext, setChatContext] = useState({
    showContext: false,
    showSuggestions: false,
    showUser: false,
    placeholder: "Ask about incidents...",
    placeholderText: "Start a conversation to get assistance",
    incidentContext: {},
  });

  const [query, setQuery] = useState("");
  const [threadId, setThreadId] = useState(null);

  const [messages, setMessage] = useState([]);

  // dummy messages for testing
  // uncomment this and comment above defn
  // const [messages, setMessage] = useState([
  //   { role: "user", message: "Hi Bot!" },
  //   { role: "bot", message: "Hi, Bro" },
  //   { role: "user", message: "How're you doing?" },
  //   { role: "bot", message: "Fine, thanks!" },
  // ]);

  const sendQuery = async () => {
    try {
      if (!query) {
        console.warn("Cannot send empty query");
        return;
      }
      setMessage((messages) => [...messages, { role: "user", message: query }]);
      setQuery("");
      const url = new URL("http://localhost:8000/query");
      if (threadId != null) {
        url.searchParams.set("thread_id", threadId);
      }
      const { client_id, ...metadata } = chatContext.incidentContext;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
          client_id,
          metadata,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const responseData = await response.json();
      setMessage((messages) => [
        ...messages,
        { role: "bot", message: responseData.response },
      ]);
      if (threadId == null) {
        setThreadId(responseData.thread_id);
      }
    } catch (er) {
      console.error("An error occurred:", er);
    }
  };

  const openChat = (options = {}) => {
    setChatContext((prev) => ({
      showContext: options.showContext || false,
      showSuggestions: options.showSuggestions || false,
      showUser: options.showUser || false,
      placeholder: options.placeholder || "Ask about incidents...",
      placeholderText:
        options.placeholderText || "Start a conversation to get assistance",
      incidentContext: options.incidentContext,
    }));
    setIsChatOpen(true);
  };

  const closeChat = () => {
    setIsChatOpen(false);
  };

  return (
    <ChatContext.Provider
      value={{
        isChatOpen,
        chatContext,
        query,
        messages,
        openChat,
        closeChat,
        setQuery,
        sendQuery,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
