import { createContext, useContext, useState } from "react";

const ChatContext = createContext();

const INCIDENT_THREAD_MAPPING_KEY = "incident-chat-mapping";

const DEFAULT_CHAT_CONTEXT = {
  showContext: false,
  showSuggestions: false,
  showUser: false,
  placeholder: "Ask about incidents...",
  placeholderText: "Start a conversation to get assistance",
  incidentContext: {},
};

const getIncidentThreadMapping = () => {
  try {
    return JSON.parse(
      localStorage.getItem(INCIDENT_THREAD_MAPPING_KEY) || "{}",
    );
  } catch (error) {
    console.error("Failed to read incident-thread mapping:", error);
    return {};
  }
};

const getThreadIdForIncident = (incidentId) => {
  if (!incidentId) return null;

  const mapping = getIncidentThreadMapping();

  return mapping[incidentId] ?? null;
};

const saveThreadIdForIncident = (incidentId, threadId) => {
  if (!incidentId || !threadId) return;

  const mapping = getIncidentThreadMapping();

  mapping[incidentId] = threadId;

  localStorage.setItem(INCIDENT_THREAD_MAPPING_KEY, JSON.stringify(mapping));
};

const getThreadMessages = (threadId) => {
  if (!threadId) return [];

  try {
    return JSON.parse(localStorage.getItem(`chat-thread-${threadId}`) || "[]");
  } catch (error) {
    console.error("Failed to read thread messages:", error);
    return [];
  }
};

const saveThreadMessages = (threadId, messages) => {
  if (!threadId) return;

  localStorage.setItem(`chat-thread-${threadId}`, JSON.stringify(messages));
};

export function ChatProvider({ children }) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatContext, setChatContext] = useState(DEFAULT_CHAT_CONTEXT);
  const [query, setQuery] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingContext, setIsLoadingContext] = useState(false);
  const [isBotLoading, setIsBotLoading] = useState(false);

  const loadIncidentContext = async (
    incidentContext,
    existingThreadId = null,
  ) => {
    const incidentId = incidentContext?.id;
    const clientId = incidentContext?.client_id;

    if (!incidentId || !clientId) {
      console.warn(
        "Cannot load incident context without incident ID and client ID",
      );
      return existingThreadId;
    }

    setIsLoadingContext(true);

    const url = new URL("http://localhost:8000/query");

    if (existingThreadId != null) {
      url.searchParams.set("thread_id", existingThreadId);
    }

    const { client_id, ...metadata } = incidentContext;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query:
            "Load the context for this incident. Review the client context and applicable SLA/priority requirements, and summarize the key information I should know before investigating the incident. Do not troubleshoot yet or make assumptions beyond the retrieved information.",
          client_id,
          metadata,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const responseData = await response.json();

      const botMessage = {
        role: "bot",
        message: responseData.message,
        resources: responseData.resources ?? [],
      };

      const newThreadId = existingThreadId ?? responseData.thread_id;

      if (newThreadId) {
        setThreadId(newThreadId);
        saveThreadIdForIncident(incidentId, newThreadId);
      }

      const updatedMessages = [botMessage];

      setMessages(updatedMessages);
      saveThreadMessages(newThreadId, updatedMessages);
      return newThreadId;
    } catch (error) {
      console.error("Failed to load incident context:", error);
      return existingThreadId;
    } finally {
      setIsLoadingContext(false);
    }
  };

  const openChat = async (options = {}) => {
    const incidentContext = options.incidentContext || {};
    const incidentId = incidentContext.id;

    const existingThreadId = getThreadIdForIncident(incidentId);
    const existingMessages = getThreadMessages(existingThreadId);

    setChatContext({
      showContext: options.showContext || false,
      showSuggestions: options.showSuggestions || false,
      showUser: options.showUser || false,
      placeholder: options.placeholder || "Ask about incidents...",
      placeholderText:
        options.placeholderText || "Start a conversation to get assistance",
      incidentContext,
    });

    setThreadId(existingThreadId);
    setMessages(existingMessages);
    setIsLoadingContext(Boolean(!existingThreadId && incidentId));

    setIsChatOpen(true);

    // Automatically load incident context only for a new incident thread.
    if (!existingThreadId && incidentId) {
      try {
        await loadIncidentContext(incidentContext);
      } catch (error) {
        console.error("Failed to load incident context:", error);
      }
    }
  };

  const closeChat = () => {
    setIsChatOpen(false);
  };

  const sendQuery = async () => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      console.warn("Cannot send empty query");
      return;
    }

    const incidentId = chatContext.incidentContext?.id;

    if (!incidentId) {
      console.warn("Cannot send query without an incident ID");
      return;
    }

    const userMessage = {
      role: "user",
      message: trimmedQuery,
      resources: [],
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setQuery("");
    setIsBotLoading(true);

    try {
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
          query: trimmedQuery,
          client_id,
          metadata,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const responseData = await response.json();

      const botMessage = {
        role: "bot",
        message: responseData.message,
        resources: responseData.resources ?? [],
      };

      const newThreadId = threadId ?? responseData.thread_id;

      if (threadId == null && newThreadId != null) {
        setThreadId(newThreadId);

        saveThreadIdForIncident(incidentId, newThreadId);
      }

      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages, botMessage];

        saveThreadMessages(newThreadId, updatedMessages);

        return updatedMessages;
      });
    } catch (error) {
      console.error("An error occurred:", error);
    } finally {
      setIsBotLoading(false);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        isChatOpen,
        chatContext,
        query,
        messages,
        threadId,
        isLoadingContext,
        isBotLoading,
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
