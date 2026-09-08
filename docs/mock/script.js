// Mock data for incidents
const incidents = [
    {
        id: 'INC-1042',
        description: 'Payment API returning 5xx errors',
        client: 'Acme Financial Services',
        assignment: { initials: 'RS', name: 'Rahul Shah' },
        status: 'open',
        lastUpdated: '5 minutes ago'
    },
    {
        id: 'INC-001',
        description: 'Server overload in US-East region',
        client: 'Acme Corp',
        assignment: { initials: 'JS', name: 'John Smith' },
        status: 'open',
        lastUpdated: '2 minutes ago'
    },
    {
        id: 'INC-002',
        description: 'Database connection timeout',
        client: 'TechStart Inc',
        assignment: { initials: 'MJ', name: 'Mary Johnson' },
        status: 'in-progress',
        lastUpdated: '15 minutes ago'
    },
    {
        id: 'INC-003',
        description: 'API rate limiting errors',
        client: 'GlobalBank',
        assignment: { initials: 'RW', name: 'Robert Wilson' },
        status: 'resolved',
        lastUpdated: '1 hour ago'
    },
    {
        id: 'INC-004',
        description: 'Memory leak in payment service',
        client: 'Shopify Plus',
        assignment: { initials: 'AL', name: 'Alice Lee' },
        status: 'open',
        lastUpdated: '3 hours ago'
    },
    {
        id: 'INC-005',
        description: 'SSL certificate expiring soon',
        client: 'Acme Corp',
        assignment: { initials: 'JD', name: 'John Doe' },
        status: 'in-progress',
        lastUpdated: '5 hours ago'
    },
    {
        id: 'INC-006',
        description: 'Cache invalidation issues',
        client: 'TechStart Inc',
        assignment: { initials: 'KB', name: 'Karen Brown' },
        status: 'resolved',
        lastUpdated: '1 day ago'
    },
    {
        id: 'INC-007',
        description: 'Login authentication failures',
        client: 'GlobalBank',
        assignment: { initials: 'TM', name: 'Tom Miller' },
        status: 'open',
        lastUpdated: '2 days ago'
    },
    {
        id: 'INC-008',
        description: 'File upload size limit exceeded',
        client: 'Shopify Plus',
        assignment: { initials: 'SJ', name: 'Sarah Jones' },
        status: 'in-progress',
        lastUpdated: '3 days ago'
    }
];

// Detailed incident data for the detail page
const incidentDetails = {
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

// Function to render incidents list
function renderIncidents(data) {
    const container = document.getElementById('incidents-body');
    container.innerHTML = '';

    data.forEach(incident => {
        const row = document.createElement('div');
        row.className = 'incident-row';
        row.style.cursor = 'pointer';
        
        const statusClass = `status-${incident.status.toLowerCase().replace(' ', '-')}`;
        const statusLabel = incident.status.charAt(0).toUpperCase() + incident.status.slice(1).replace('-', ' ');

        row.innerHTML = `
            <div class="cell cell-id">${incident.id}</div>
            <div class="cell cell-description">${incident.description}</div>
            <div class="cell cell-client">${incident.client}</div>
            <div class="cell cell-assignment">
                <div class="assignment-avatar">${incident.assignment.initials}</div>
                <span class="assignment-name">${incident.assignment.name}</span>
            </div>
            <div class="cell cell-status">
                <span class="status-badge ${statusClass}">
                    <span class="status-dot"></span>
                    ${statusLabel}
                </span>
            </div>
            <div class="cell cell-updated">${incident.lastUpdated}</div>
        `;

        // Add click event to navigate to incident detail
        row.addEventListener('click', () => {
            window.location.href = `incident.html?id=${incident.id}`;
        });

        container.appendChild(row);
    });
}

// Function to filter incidents based on search
function filterIncidents(searchTerm, statusFilter) {
    let filtered = incidents;

    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(incident => 
            incident.id.toLowerCase().includes(term) ||
            incident.description.toLowerCase().includes(term) ||
            incident.client.toLowerCase().includes(term)
        );
    }

    if (statusFilter && statusFilter !== 'All statuses') {
        filtered = filtered.filter(incident => 
            incident.status.toLowerCase() === statusFilter.toLowerCase()
        );
    }

    renderIncidents(filtered);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    renderIncidents(incidents);

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('input', (e) => {
        const statusFilter = document.querySelector('.status-filter').value;
        filterIncidents(e.target.value, statusFilter);
    });

    // Status filter functionality
    const statusSelect = document.querySelector('.status-filter');
    statusSelect.addEventListener('change', (e) => {
        const searchTerm = document.querySelector('.search-input').value;
        filterIncidents(searchTerm, e.target.value);
    });

    // Chat sidebar functionality
    const headerSparkleBtn = document.getElementById('header-sparkle-btn');
    const chatSidebar = document.getElementById('chat-sidebar');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatPlaceholder = document.getElementById('chat-placeholder');
    const chatMessages = document.getElementById('chat-messages');

    if (headerSparkleBtn && chatSidebar) {
        headerSparkleBtn.addEventListener('click', () => {
            chatSidebar.classList.add('open');
            
            // Initialize chat with general context
            if (chatPlaceholder && chatMessages) {
                chatPlaceholder.style.display = 'none';
                chatMessages.style.display = 'flex';
                
                // Only add messages if chat is empty
                if (chatMessages.children.length === 0) {
                    initializeGeneralChat();
                }
            }
        });
    }

    if (chatCloseBtn && chatSidebar) {
        chatCloseBtn.addEventListener('click', () => {
            chatSidebar.classList.remove('open');
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (chatSidebar && chatSidebar.classList.contains('open')) {
            if (!chatSidebar.contains(e.target) && !headerSparkleBtn.contains(e.target)) {
                chatSidebar.classList.remove('open');
            }
        }
    });
});

// Function to initialize general chat (for dashboard)
function initializeGeneralChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    // Create general info drawer
    addGeneralInfoDrawer();

    // Show thinking indicator
    const thinkingId = addThinkingIndicator();

    // Simulate bot thinking for 3 seconds
    setTimeout(() => {
        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);
        
        // Add bot response with interactive buttons
        const botResponse = `I can help you with incident management by searching through our knowledge base. I have access to:

• SLAs and service level agreements for all clients
• Comprehensive runbooks and troubleshooting procedures
• Client-specific configurations and constraints
• Historical incident patterns and solutions`;
        
        const options = [
            { id: 'analyze', text: 'Analyze a specific incident' },
            { id: 'search', text: 'Search for procedures' },
            { id: 'guidance', text: 'Create a guidance document for incident resolution' }
        ];
        
        const sources = [
            'Incident Dashboard Context',
            'ITSM Knowledge Base',
            'Service Level Agreements'
        ];
        
        addMessage(botResponse, 'lambda', options, sources);
    }, 3000);
}

// Function to add general info drawer (for dashboard)
function addGeneralInfoDrawer() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const drawerDiv = document.createElement('div');
    drawerDiv.className = 'incident-info-drawer';

    const drawerHeader = document.createElement('div');
    drawerHeader.className = 'drawer-header';
    drawerHeader.innerHTML = `
        <div class="drawer-title">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 0L9.5 5.5L15 7L9.5 8.5L8 14L6.5 8.5L1 7L6.5 5.5L8 0Z" fill="#1c1c1c"/>
            </svg>
            <span>Context Info</span>
        </div>
        <svg class="drawer-chevron" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="#1c1c1c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `;

    const drawerContent = document.createElement('div');
    drawerContent.className = 'drawer-content';
    drawerContent.style.display = 'none';

    // Create table with general information
    const table = document.createElement('table');
    table.className = 'incident-info-table';

    const generalData = [
        { label: 'View', value: 'Incident Dashboard' },
        { label: 'Context', value: 'Incident Management' },
        { label: 'Active Incidents', value: incidents.length.toString() },
        { label: 'Filter', value: 'Operational incidents only' }
    ];

    generalData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="table-label">${item.label}</td>
            <td class="table-value">${item.value}</td>
        `;
        table.appendChild(row);
    });

    drawerContent.appendChild(table);
    drawerDiv.appendChild(drawerHeader);
    drawerDiv.appendChild(drawerContent);
    chatMessages.appendChild(drawerDiv);

    // Toggle drawer on click
    drawerHeader.addEventListener('click', () => {
        const isExpanded = drawerContent.style.display !== 'none';
        drawerContent.style.display = isExpanded ? 'none' : 'block';
        drawerHeader.querySelector('.drawer-chevron').style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
    });

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

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
        avatarDiv.textContent = 'JD';
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = text.replace(/\n/g, '<br>');

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
        if (option.id === 'analyze') {
            response = `To analyze a specific incident, please click on any incident from the dashboard. I'll then provide detailed analysis including:

• SLA compliance status
• Relevant runbooks and procedures
• Client-specific considerations
• Historical pattern matching

Open an incident and I'll be ready to help!`;
            
            sources = [
                'Incident Dashboard Context',
                'ITSM Knowledge Base',
                'Service Level Agreements'
            ];
        } else if (option.id === 'search') {
            response = `I can search through our knowledge base for:

• Specific runbooks by service or incident type
• Client procedures and configurations
• SLA documentation
• Historical incident solutions

What would you like me to search for? Please provide keywords or describe what you're looking for.`;
            
            sources = [
                'ITSM Knowledge Base',
                'Service Documentation',
                'Historical Incident Database'
            ];
        } else if (option.id === 'guidance') {
            response = `I can create comprehensive guidance documents for incident resolution. This includes:

• Immediate action steps
• Investigation procedures
• Resolution workflows
• Post-resolution follow-up tasks

To create a specific guidance document, please open an incident first. I'll then generate a tailored resolution plan based on the incident details, client requirements, and service-specific procedures.

The guidance document will be structured, actionable, and aligned with your organization's incident management protocols.`;
            
            sources = [
                'ITSM Resolution Protocols',
                'Service Level Agreements',
                'Client Procedures Database'
            ];
        }
        
        addMessage(response, 'lambda', null, sources);
    }, 2000);
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
    const thinkingElement = document.getElementById(thinkingId);
    if (thinkingElement) {
        thinkingElement.remove();
    }
}
