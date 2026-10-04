import { useChat } from "../../context/ChatContext";

function ChatSuggestions() {
  const { query, setQuery } = useChat();

  const allSuggestions = [
    // SLA & Priority
    "Explain the SLAs for this incident",
    "What are the response targets for P1 incidents?",
    "Show me the SLA compliance requirements",
    "What are the priority levels and their definitions?",
    "How does the SLA affect this incident timeline?",

    // Troubleshooting
    "What are the common causes for this issue?",
    "Prepare a troubleshooting guide",
    "What diagnostic steps should I take?",
    "Check if there are any recent changes",
    "Analyze the error patterns and logs",

    // Escalation & Contacts
    "Who should I escalate this to?",
    "Show me the escalation path",
    "What are the special instructions for this client?",
    "Contact information for emergency escalation",
    "When should I involve customer IT?",

    // Documentation & Resources
    "Prepare a guidance document",
    "Find relevant runbooks for this issue",
    "Search for similar past incidents",
    "What documentation exists for this system?",
    "Retrieve operational procedures",

    // Impact & Scope
    "What systems are affected?",
    "Assess the business impact",
    "Which services are in scope?",
    "Check critical system dependencies",
    "What is the current incident scope?",

    // Next Steps
    "What are the next steps?",
    "Create an action plan",
    "Prioritize the investigation tasks",
    "What should I communicate to stakeholders?",
    "How to document the progress?",

    // Context & History
    "Summarize what we know so far",
    "What has been tried already?",
    "Show me the incident timeline",
    "What context is already loaded?",
    "Review the client configuration",

    // Resolution
    "How to verify the fix?",
    "Prepare a post-incident report",
    "What are the closure criteria?",
    "Document the root cause",
    "Update the incident status",

    // General
    "Help me investigate this incident",
    "What information do I need to gather?",
    "Is there a standard procedure for this?",
    "What tools should I use?",
    "How to track this investigation?",
  ];

  // Filter suggestions based on query
  const getFilteredSuggestions = () => {
    if (!query || query.trim().length === 0) {
      // Show random 3 when no query
      return allSuggestions.slice(0, 3);
    }

    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);

    // Score each suggestion based on word matches
    const scored = allSuggestions.map(suggestion => {
      const suggestionLower = suggestion.toLowerCase();
      let score = 0;

      // Exact query match gets highest score
      if (suggestionLower.includes(queryLower)) {
        score += 10;
      }

      // Word matches
      queryWords.forEach(word => {
        if (suggestionLower.includes(word)) {
          score += 5;
        }
      });

      // Partial word matches
      queryWords.forEach(word => {
        const partial = word.slice(0, 4);
        if (partial.length >= 3 && suggestionLower.includes(partial)) {
          score += 2;
        }
      });

      return { suggestion, score };
    });

    // Sort by score and take top 3
    return scored
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(item => item.suggestion);
  };

  const filteredSuggestions = getFilteredSuggestions();

  return (
    <div className="chat-suggestions">
      {filteredSuggestions.map((suggestion, index) => (
        <button
          key={index}
          className="suggestion-btn flex items-center gap-1.5 hover:bg-[#fafafa]/70 transition-all"
          onClick={() => setQuery(suggestion)}
        >
          <span>{suggestion}</span>
        </button>
      ))}
    </div>
  );
}

export default ChatSuggestions;

