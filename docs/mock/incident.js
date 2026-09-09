// Detailed incident data for the detail page
const incidentDetails = {
    'INC-1042': {
        id: 'INC-1042',
        title: 'Payment API returning 5xx errors',
        status: 'Investigating',
        client: 'Acme Financial Services',
        assignment: 'Platform Support',
        service: 'Payment API',
        priority: 'P1 - Critical',
        description: 'Production Payment API is returning elevated HTTP 502 responses. Database connection failures are visible in application logs.',
        activities: [
            { author: 'Monitoring', time: '09:42 UTC', message: 'Elevated 502 responses detected on the production service.' },
            { author: 'Rahul Shah', time: '09:47 UTC', message: 'Initial investigation indicates a service dependency failure.' },
            { author: 'Monitoring', time: '09:53 UTC', message: 'Error rate increased. Incident priority confirmed as P1.' },
            { author: 'Rahul Shah', time: '10:01 UTC', message: 'Database connection pool exhaustion identified.' }
        ]
    },
    'INC-001': {
        id: 'INC-001',
        title: 'Server overload in US-East region',
        status: 'Investigating',
        client: 'Acme Corp',
        assignment: 'Platform Support',
        service: 'Compute Service',
        priority: 'P2 - High',
        description: 'Server overload detected in US-East region causing elevated response times. CPU utilization is at 95% across multiple instances.',
        activities: [
            { author: 'Monitoring', time: '09:42 UTC', message: 'Elevated CPU utilization detected on US-East servers.' },
            { author: 'John Smith', time: '09:47 UTC', message: 'Initial investigation indicates traffic spike from new customer onboarding.' },
            { author: 'Monitoring', time: '09:53 UTC', message: 'Auto-scaling triggered. Additional instances provisioning.' }
        ]
    },
    'INC-002': {
        id: 'INC-002',
        title: 'Database connection timeout',
        status: 'Investigating',
        client: 'TechStart Inc',
        assignment: 'Database Team',
        service: 'Primary Database',
        priority: 'P1 - Critical',
        description: 'Database connection timeouts occurring intermittently. Connection pool exhaustion suspected.',
        activities: [
            { author: 'Monitoring', time: '10:15 UTC', message: 'Database connection timeout rate elevated above threshold.' },
            { author: 'Mary Johnson', time: '10:22 UTC', message: 'Connection pool metrics showing max utilization.' },
            { author: 'Monitoring', time: '10:30 UTC', message: 'Incident priority escalated to P1 due to customer impact.' }
        ]
    },
    'INC-003': {
        id: 'INC-003',
        title: 'API rate limiting errors',
        status: 'Resolved',
        client: 'GlobalBank',
        assignment: 'API Gateway Team',
        service: 'API Gateway',
        priority: 'P3 - Medium',
        description: 'API rate limiting errors being returned to valid requests. Rate limiter configuration needs review.',
        activities: [
            { author: 'Monitoring', time: '08:00 UTC', message: 'Rate limiting errors detected on API endpoints.' },
            { author: 'Robert Wilson', time: '08:15 UTC', message: 'Rate limiter rules misconfigured for enterprise tier.' },
            { author: 'Robert Wilson', time: '09:00 UTC', message: 'Configuration updated. Monitoring for resolution.' },
            { author: 'Monitoring', time: '09:30 UTC', message: 'Error rates returned to normal. Incident resolved.' }
        ]
    },
    'INC-004': {
        id: 'INC-004',
        title: 'Memory leak in payment service',
        status: 'Investigating',
        client: 'Shopify Plus',
        assignment: 'Payment Team',
        service: 'Payment Service',
        priority: 'P1 - Critical',
        description: 'Memory leak detected in payment service causing gradual degradation and eventual service restarts.',
        activities: [
            { author: 'Monitoring', time: '11:00 UTC', message: 'Memory usage trending upward on payment service instances.' },
            { author: 'Alice Lee', time: '11:15 UTC', message: 'Memory profiler indicates leak in transaction processing module.' }
        ]
    },
    'INC-005': {
        id: 'INC-005',
        title: 'SSL certificate expiring soon',
        status: 'Investigating',
        client: 'Acme Corp',
        assignment: 'Security Team',
        service: 'Load Balancer',
        priority: 'P2 - High',
        description: 'SSL certificate for production load balancer expiring in 7 days. Renewal process needs to be initiated.',
        activities: [
            { author: 'Monitoring', time: '07:00 UTC', message: 'SSL certificate expiration warning triggered.' },
            { author: 'John Doe', time: '07:30 UTC', message: 'Certificate renewal ticket created with security team.' }
        ]
    },
    'INC-006': {
        id: 'INC-006',
        title: 'Cache invalidation issues',
        status: 'Resolved',
        client: 'TechStart Inc',
        assignment: 'Cache Team',
        service: 'Redis Cache',
        priority: 'P3 - Medium',
        description: 'Cache invalidation not propagating correctly across distributed cache nodes causing stale data.',
        activities: [
            { author: 'Monitoring', time: '06:00 UTC', message: 'Cache inconsistency detected across nodes.' },
            { author: 'Karen Brown', time: '06:30 UTC', message: 'Invalidation protocol version mismatch identified.' },
            { author: 'Karen Brown', time: '08:00 UTC', message: 'Protocol updated across all cache nodes. Incident resolved.' }
        ]
    },
    'INC-007': {
        id: 'INC-007',
        title: 'Login authentication failures',
        status: 'Investigating',
        client: 'GlobalBank',
        assignment: 'Auth Team',
        service: 'Authentication Service',
        priority: 'P1 - Critical',
        description: 'Elevated login authentication failures across user base. Possible token service issue.',
        activities: [
            { author: 'Monitoring', time: '12:00 UTC', message: 'Authentication failure rate elevated above normal baseline.' },
            { author: 'Tom Miller', time: '12:15 UTC', message: 'Token validation service showing increased latency.' }
        ]
    },
    'INC-008': {
        id: 'INC-008',
        title: 'File upload size limit exceeded',
        status: 'Investigating',
        client: 'Shopify Plus',
        assignment: 'Storage Team',
        service: 'File Upload Service',
        priority: 'P2 - High',
        description: 'File upload size limit being enforced incorrectly. Valid uploads within limits are being rejected.',
        activities: [
            { author: 'Monitoring', time: '13:00 UTC', message: 'File upload rejection rate increased for valid files.' },
            { author: 'Sarah Jones', time: '13:20 UTC', message: 'Size validation logic error identified in middleware.' }
        ]
    }
};

// Get incident ID from URL parameter
function getIncidentIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

// Function to get initials from name
function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

// Function to render activity thread
function renderActivityThread(activities) {
    const container = document.getElementById('activity-thread');
    container.innerHTML = '';

    activities.forEach((activity, index) => {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const initials = getInitials(activity.author);
        
        item.innerHTML = `
            <div class="activity-avatar">${initials}</div>
            <div class="activity-content">
                <div class="activity-header">
                    <span class="activity-author">${activity.author}</span>
                    <span class="activity-time">${activity.time}</span>
                </div>
                <div class="activity-message">${activity.message}</div>
            </div>
        `;
        
        container.appendChild(item);
    });
}

// Function to populate incident details
function populateIncidentDetails(incidentId) {
    const incident = incidentDetails[incidentId];
    
    if (!incident) {
        // Default to a sample incident if not found
        return;
    }

    document.getElementById('detail-id').textContent = incident.id;
    document.getElementById('detail-title').textContent = incident.title;
    document.getElementById('detail-status').textContent = incident.status;
    document.getElementById('detail-client').textContent = incident.client;
    document.getElementById('detail-assignment').textContent = incident.assignment;
    document.getElementById('detail-service').textContent = incident.service;
    document.getElementById('detail-priority').textContent = incident.priority;
    document.getElementById('detail-description').textContent = incident.description;

    renderActivityThread(incident.activities);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    const incidentId = getIncidentIdFromUrl();
    if (incidentId) {
        populateIncidentDetails(incidentId);
    } else {
        // Default to INC-1042 (the one from the image) if no ID provided
        populateIncidentDetails('INC-1042');
    }

    // Chat sidebar functionality
    const sparkleBtn = document.getElementById('sparkle-btn');
    const chatSidebar = document.getElementById('chat-sidebar');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatPlaceholder = document.getElementById('chat-placeholder');
    const chatMessages = document.getElementById('chat-messages');
    const mainContent = document.getElementById('main-content');

    if (sparkleBtn && chatSidebar) {
        sparkleBtn.addEventListener('click', () => {
            chatSidebar.classList.add('open');
            if (mainContent) {
                mainContent.classList.add('shifted');
            }
            
            // Initialize chat with incident context
            if (chatPlaceholder && chatMessages) {
                chatPlaceholder.style.display = 'none';
                chatMessages.style.display = 'flex';
                
                // Only add messages if chat is empty
                if (chatMessages.children.length === 0) {
                    const incident = incidentDetails[incidentId] || incidentDetails['INC-1042'];
                    initializeChat(incident);
                }
            }
        });
    }

    if (chatCloseBtn && chatSidebar) {
        chatCloseBtn.addEventListener('click', () => {
            chatSidebar.classList.remove('open');
            if (mainContent) {
                mainContent.classList.remove('shifted');
            }
        });
    }

    // Close sidebar when clicking outside (but not for push layout)
    // For push layout, we keep the sidebar open until explicitly closed

    // Context section collapsible functionality
    const contextSectionHeaders = document.querySelectorAll('.context-section-header');
    contextSectionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const sectionBody = header.nextElementSibling;
            if (sectionBody && sectionBody.classList.contains('context-section-body')) {
                // Toggle collapsed state
                header.classList.toggle('collapsed');
                sectionBody.classList.toggle('collapsed');
            }
        });
    });

    // Main context collapse functionality
    const mainContextHeader = document.getElementById('main-context-header');
    const mainContextContent = document.getElementById('main-context-content');
    
    if (mainContextHeader && mainContextContent) {
        mainContextHeader.addEventListener('click', () => {
            mainContextHeader.classList.toggle('collapsed');
            mainContextContent.classList.toggle('collapsed');
        });
    }

    // Suggestion buttons functionality
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const suggestion = btn.getAttribute('data-suggestion');
            handleSuggestionClick(suggestion);
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

// Function to initialize chat with incident context
function initializeChat(incident) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    // Show thinking indicator
    const thinkingId = addThinkingIndicator();

    // Simulate bot thinking for 3 seconds
    setTimeout(() => {
        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);
        
        // Add bot response with simple welcome message
        const botResponse = `I've reviewed the context for ${incident.id}. I can help with the applicable SLA, client procedures, and relevant runbooks.`;
        
        addMessage(botResponse, 'lambda');
    }, 3000);
}

// Function to add incident info drawer (removed - not needed in simplified version)

// Function to add a message to the chat
function addMessage(text, sender, options = null, sources = null) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return null;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (sender === 'lambda') {
        avatarDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 4L12 20L20 4" stroke="#1c1c1c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    } else {
        avatarDiv.textContent = 'AR';
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Handle markdown-style formatting
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
        .replace(/\n/g, '<br>'); // Line breaks
    
    textDiv.innerHTML = formattedText;

    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    // Add sources if provided
    if (sources && sender === 'lambda') {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        
        const sourcesLabel = document.createElement('div');
        sourcesLabel.className = 'sources-label';
        sourcesLabel.textContent = 'Sources:';
        
        const sourcesList = document.createElement('ul');
        sourcesList.className = 'sources-list';
        
        sources.forEach(source => {
            const sourceItem = document.createElement('li');
            sourceItem.textContent = source;
            sourcesList.appendChild(sourceItem);
        });
        
        sourcesDiv.appendChild(sourcesLabel);
        sourcesDiv.appendChild(sourcesList);
        contentDiv.appendChild(sourcesDiv);
    }

    // Add interactive buttons if provided
    if (options && sender === 'lambda') {
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

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

// Function to handle suggestion button clicks
function handleSuggestionClick(suggestion) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    // Add user message with the suggestion
    addMessage(suggestion, 'user');

    // Show thinking indicator
    const thinkingId = addThinkingIndicator();

    // Simulate bot response based on suggestion
    setTimeout(() => {
        removeThinkingIndicator(thinkingId);
        
        let response = '';
        
        const incidentId = document.getElementById('detail-id').textContent;
        const client = document.getElementById('detail-client').textContent;
        const service = document.getElementById('detail-service').textContent;
        const priority = document.getElementById('detail-priority').textContent;
        
        if (suggestion === 'Prepare a guidance document') {
            response = `Here's a guidance document for resolving ${incidentId}:

**INCIDENT RESOLUTION GUIDANCE**
Incident: ${incidentId}
Service: ${service}
Priority: ${priority}
Client: ${client}

**IMMEDIATE ACTIONS**
• Assess current impact and affected users
• Verify error rates and service degradation
• Check recent deployments or configuration changes

**INVESTIGATION STEPS**
• Review application logs for error patterns
• Check system metrics (CPU, memory, disk, network)
• Verify database connectivity and performance
• Analyze recent code changes or deployments

**RESOLUTION PROCEDURES**
• Follow the ${service} runbook
• Apply client-specific recovery procedures
• Test resolution in staging environment first
• Deploy fix to production with monitoring`;
        } else if (suggestion === 'Explain the SLAs') {
            response = `Here are the applicable SLAs for this incident:

**SERVICE LEVEL AGREEMENTS**
Incident: ${incidentId}
Priority: ${priority}

**RESPONSE TIME SLA**
• P1 - Critical: 15 minutes initial response
• P2 - High: 30 minutes initial response
• P3 - Medium: 1 hour initial response

**RESOLUTION TIME SLA**
• P1 - Critical: 4 hours to resolution
• P2 - High: 8 hours to resolution
• P3 - Medium: 24 hours to resolution

**CLIENT-SPECIFIC SLAS**
${client} has enhanced SLA terms:
• Priority support for all incidents
• Dedicated support channel for P1 incidents
• Monthly incident review meetings`;
        } else if (suggestion === 'What are the next steps?') {
            response = `Based on the incident context, here are the recommended next steps:

**IMMEDIATE NEXT STEPS**
1. Check ${service} health dashboard
2. Review current error rates and saturation
3. Verify database connectivity
4. Check recent deployments or configuration changes

**INVESTIGATION STEPS**
• Review application logs for error patterns
• Analyze system metrics (CPU, memory, disk, network)
• Check connection pool utilization
• Verify client-specific recovery configuration

**RESOLUTION PROCEDURES**
• Follow the ${service} Production Runbook
• Apply appropriate recovery procedures
• Coordinate with service owner for production changes
• Monitor for 30 minutes after resolution`;
        } else {
            response = `I can help you with that. Let me provide information based on the incident context for ${incidentId}.`;
        }
        
        addMessage(response, 'lambda');
    }, 2000);
}

// Function to handle option button clicks (removed - not needed in simplified version)

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
    const thinkingElement = document.getElementById(thinkingId);
    if (thinkingElement) {
        thinkingElement.remove();
    }
}
