export const knowledgeSources = [
  {
    id: 1,
    title: 'Client-Onboarding Documentation',
    subtitle: 'CODs',
    source: 'Drive Files',
    description: 'Comprehensive documentation for new client onboarding including IT environment, applications, infrastructure, and architecture details.',
    details: {
      label: 'Includes:',
      value: 'Client details, IT environment, Applications, Infrastructure, Architecture & Dependencies, Monitoring & Observability, Escalations',
    },
    action: 'Browse Documents',
    icon: 'document',
  },
  {
    id: 2,
    title: 'Runbooks',
    subtitle: 'Operational Procedures',
    source: 'Internal Wiki',
    description: 'Step-by-step instructions for performing specific operational tasks and responding to particular incidents with standardized procedures.',
    details: {
      label: 'Coverage:',
      value: 'Incident response, system maintenance, troubleshooting procedures, deployment guides',
    },
    action: 'Access Wiki',
    icon: 'layers',
  },
  {
    id: 3,
    title: 'Service-Level Agreements',
    subtitle: 'SLAs',
    source: 'Database API',
    description: 'Service level commitments with measurable time targets for response and resolution times across different priority levels.',
    details: {
      label: 'Metrics:',
      value: 'Response time, resolution time, uptime guarantees, penalty clauses',
    },
    action: 'View SLAs',
    icon: 'clock',
  },
]