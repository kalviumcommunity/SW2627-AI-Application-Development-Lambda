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
  const [error, setError] = useState(null);

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
            "Load the context for this incident. Retrieve the client context, SLAs, and relevant information. Do not troubleshoot or summarize. Just return: 'I have reviewed the incident, all set.'",
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
      setError("Failed to load incident context. Please try again.");
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

  const startNewThread = async () => {
    const incidentId = chatContext.incidentContext?.id;
    const currentThreadId = threadId;

    if (incidentId) {
      const mapping = getIncidentThreadMapping();
      delete mapping[incidentId];
      localStorage.setItem(INCIDENT_THREAD_MAPPING_KEY, JSON.stringify(mapping));
    }

    if (currentThreadId) {
      localStorage.removeItem(`chat-thread-${currentThreadId}`);
    }

    setThreadId(null);
    setMessages([]);

    // Reload incident context for the new thread
    if (incidentId) {
      try {
        await loadIncidentContext(chatContext.incidentContext);
      } catch (error) {
        console.error("Failed to load incident context for new thread:", error);
      }
    }
  };

  const pruneLocalStorage = () => {
    const incidentId = chatContext.incidentContext?.id;
    const currentThreadId = threadId;

    const mapping = getIncidentThreadMapping();
    const currentIncidentThreadId = incidentId ? mapping[incidentId] : null;

    Object.keys(mapping).forEach((key) => {
      if (key !== incidentId) {
        const threadIdToDelete = mapping[key];
        if (threadIdToDelete) {
          localStorage.removeItem(`chat-thread-${threadIdToDelete}`);
        }
        delete mapping[key];
      }
    });

    localStorage.setItem(INCIDENT_THREAD_MAPPING_KEY, JSON.stringify(mapping));

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith("chat-thread-") && key !== `chat-thread-${currentThreadId}`) {
        localStorage.removeItem(key);
      }
    }
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

    setError(null);

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
      setError("Failed to send message. Please check your connection and try again.");
      setMessages((prevMessages) => {
        const errorMessage = {
          role: "bot",
          message: "Sorry, I encountered an error. Please try again.",
          resources: [],
        };
        return [...prevMessages, errorMessage];
      });
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
        error,
        openChat,
        closeChat,
        setQuery,
        sendQuery,
        startNewThread,
        pruneLocalStorage,
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
