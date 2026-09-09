// Knowledge page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Chat sidebar functionality - removed header sparkle button
    const chatSidebar = document.getElementById('chat-sidebar');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatInput = document.querySelector('.chat-input');
    const chatSubmitBtn = document.querySelector('.chat-submit-btn');
    const chatPlaceholder = document.getElementById('chat-placeholder');
    const chatMessages = document.getElementById('chat-messages');

    // Close chat sidebar
    chatCloseBtn.addEventListener('click', function() {
        chatSidebar.classList.remove('open');
    });

    // Handle chat input
    function handleChatSubmit() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Hide placeholder and show messages
        chatPlaceholder.style.display = 'none';
        chatMessages.style.display = 'flex';

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Simulate AI response
        setTimeout(() => {
            const responses = [
                {
                    text: "I can help you find information in our knowledge base. What would you like to know about?",
                    sources: ['CODs: Client Documentation', 'Runbooks: Operational Procedures', 'SLAs: Service Agreements']
                },
                {
                    text: "Based on your query, I found relevant information in our Client-Onboarding Documentation. Would you like me to provide more details?",
                    sources: ['COD: Acme Corporation', 'Section: Infrastructure Details']
                },
                {
                    text: "I found a matching runbook for this scenario. Here are the recommended steps:",
                    sources: ['Runbook: Database Recovery', 'Internal Wiki']
                }
            ];

            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse.text, 'lambda', null, randomResponse.sources);
        }, 1000);
    }

    function addMessage(text, type, options = null, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = type === 'user' 
            ? '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="white" stroke-width="2"/></svg>'
            : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M4 4L12 20L20 4" stroke="#1c1c1c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = text.replace(/\n/g, '<br>');
        contentDiv.appendChild(textDiv);

        if (sources && type === 'lambda') {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            
            const sourcesLabel = document.createElement('div');
            sourcesLabel.className = 'sources-label';
            sourcesLabel.textContent = 'Sources';
            sourcesDiv.appendChild(sourcesLabel);

            const sourcesList = document.createElement('ul');
            sourcesList.className = 'sources-list';
            sources.forEach(source => {
                const li = document.createElement('li');
                li.textContent = source;
                sourcesList.appendChild(li);
            });
            sourcesDiv.appendChild(sourcesList);
            contentDiv.appendChild(sourcesDiv);
        }

        // Add interactive buttons if provided
        if (options && type === 'lambda') {
            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'message-options';

            options.forEach(option => {
                const button = document.createElement('button');
                button.className = 'message-option-btn';
                button.textContent = option.text;
                button.addEventListener('click', () => handleOptionClick(option));
                optionsDiv.appendChild(button);
            });

            contentDiv.appendChild(optionsDiv);
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to handle option button clicks
    function handleOptionClick(option) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        // Add user message with the selected option
        addMessage(option.text, 'user');

        // Show thinking indicator
        const thinkingId = addThinkingIndicator();

        // Simulate bot response based on option
        setTimeout(() => {
            removeThinkingIndicator(thinkingId);
            
            let response = '';
            if (option.id === 'cods') {
                response = `I can help you find client documentation. Our CODs (Client-Onboarding Documentation) contain:

• Client details (name, BU, location)
• IT environment (Cloud Provider, On-prem servers)
• Applications (CRM, web applications, databases)
• Infrastructure (Load balancers, IAMs, Servers, firewalls)
• Architecture & Dependencies
• Monitoring & Observability
• Escalation contacts

Which client are you looking for?`;
            } else if (option.id === 'runbooks') {
                response = `I can search through our runbooks from the Internal Wiki. Our runbooks cover:

• Incident response procedures
• System maintenance tasks
• Troubleshooting guides
• Deployment procedures
• Emergency recovery scenarios

What type of procedure are you looking for?`;
            } else if (option.id === 'slas') {
                response = `I can check SLA information from our database. Our SLAs include:

• Response time targets by priority level
• Resolution time commitments
• Uptime guarantees
• Client-specific terms
• Penalty clauses

Which client or service level would you like to check?`;
            } else {
                response = `I can help you with that. Let me search our knowledge base for relevant information.`;
            }
            
            addMessage(response, 'lambda');
        }, 2000);
    }

    chatSubmitBtn.addEventListener('click', handleChatSubmit);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleChatSubmit();
        }
    });

    // Card action buttons - disabled functionality
    const cardActionBtns = document.querySelectorAll('.card-action-btn');
    cardActionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            // Do nothing when clicked
        });
    });

    // Set active navigation based on current page
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});

// Function to initialize knowledge chat
function initializeKnowledgeChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    // Show thinking indicator
    const thinkingId = addThinkingIndicator();

    // Simulate bot thinking for 3 seconds
    setTimeout(() => {
        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);
        
        // Add bot response with knowledge context
        const botResponse = `I can help you navigate our knowledge base. I have access to:

• Client-Onboarding Documentation (CODs) from Drive files
• Runbooks from our Internal Wiki
• Service-Level Agreements (SLAs) from our database

What would you like to know about?`;
        
        const options = [
            { id: 'cods', text: 'Find client documentation' },
            { id: 'runbooks', text: 'Search runbooks' },
            { id: 'slas', text: 'Check SLA information' }
        ];
        
        const sources = [
            'Knowledge Base Context',
            'ITSM Documentation',
            'Service Repository'
        ];
        
        addMessage(botResponse, 'lambda', options, sources);
    }, 3000);
}

// Function to add thinking indicator
function addThinkingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return null;

    const thinkingId = 'thinking-' + Date.now();
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = thinkingId;
    thinkingDiv.className = 'chat-message lambda-message';
    
    thinkingDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 4L12 20L20 4" stroke="#1c1c1c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="thinking-indicator">
                <div class="thinking-dots">
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(thinkingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return thinkingId;
}

// Function to remove thinking indicator
function removeThinkingIndicator(thinkingId) {
    const thinkingDiv = document.getElementById(thinkingId);
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}