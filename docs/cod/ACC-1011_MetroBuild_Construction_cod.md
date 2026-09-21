# MetroBuild Construction - Client Operations Documentation

## Client Details
- **Company Name**: MetroBuild Construction
- **Account ID**: ACC-1011
- **Industry**: Construction
- **Company Size**: Large
- **Primary Region**: Australia
- **Timezone**: Australia/Sydney
- **Business Unit**: Construction Operations & Project Management

## IT Environment
- **Cloud Provider**: Microsoft Azure (australia-east)
- **On-Premises**: 15 construction sites across Australia with mobile infrastructure
- **Infrastructure Type**: Field-focused with mobile connectivity and project management

## Applications

### BuildTrack Pro
- **Description**: Project management platform handling construction schedules, resource allocation, budget tracking, and milestone management across 15 active sites
- **Type**: Construction Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, mobile APIs, BIM integration

### DocVault Construction
- **Description**: Document management system for blueprints, specifications, contracts, and compliance documents with version control and mobile access
- **Type**: Document Management
- **Criticality**: Critical
- **Technology Stack**: SharePoint, Microsoft 365, custom mobile apps

### FieldConnect Mobile
- **Description**: Field connectivity platform providing mobile internet, VoIP, and data access for construction crews at remote sites
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Cisco Meraki, 4G/5G connectivity, SD-WAN

### Office365 Suite
- **Description**: Microsoft 365 environment including Exchange Online, Teams, OneDrive, and SharePoint for corporate operations and collaboration
- **Type**: Productivity Suite
- **Criticality**: High
- **Technology Stack**: Microsoft 365, Exchange Online, SharePoint Online

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for web applications
- **Secondary**: Hardware load balancers at construction sites
- **Configuration**: Geographic routing with site-level failover

### Identity & Access Management
- **Provider**: Microsoft Azure Active Directory with construction-specific policies
- **MFA**: Microsoft Authenticator for field staff
- **Role-Based Access**: Site-based permissions with project team access controls

### Servers
- **Application Servers**: 16x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (geo-replicated)
- **Site Servers**: Ruggedized servers at construction sites
- **Cache Servers**: Azure Cache for Redis

### Firewalls & Security
- **Network Security**: Azure Firewall with construction-specific rules
- **Network Security**: Cisco firewalls at construction sites
- **Network Segmentation**: Separate subnets for project systems, field connectivity, and corporate systems
- **Compliance**: Australian construction industry standards, ISO 27001

## Architecture & Dependencies

### Application Connectivity
- **BuildTrack Pro** ↔ **DocVault Construction** ↔ Project document management
- **BuildTrack Pro** ↔ **FieldConnect Mobile** ↔ Site data synchronization
- **DocVault Construction** ↔ **Office365 Suite** ↔ Corporate collaboration
- **All systems** ↔ Azure services (logging, monitoring, storage)

### Critical Dependencies
- **BuildTrack Pro** is required for all project management operations
- **DocVault Construction** is required for document access and compliance
- **FieldConnect Mobile** is required for site connectivity
- **Mobile connectivity via 4G/5G** at construction sites

### Data Flow
- Project data → BuildTrack Pro → DocVault Construction → Document storage
- Site updates → FieldConnect Mobile → BuildTrack Pro → Project management
- Corporate collaboration → Office365 Suite → Document sharing

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with custom construction metrics
- **Site Monitoring**: Custom monitoring for field connectivity
- **Application Performance**: AppDynamics APM for construction applications
- **Network Monitoring**: Cisco SD-WAN monitoring

### Key Alerts
- **P1**: Project management system down, document management unavailable, site connectivity failure
- **P2**: Slow project data sync, document access issues, mobile connectivity problems
- **P3**: Individual application errors, backup job failures, site-specific issues

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 7 years for construction compliance
- **Site Logs**: Daily upload to central storage

## Escalations

### Primary Contacts
- **Service Manager**: Nathan Cooper (Client Service Manager)
- **Customer IT Owner**: Sophie Martin
- **Escalation Group**: MetroBuild Digital Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to MetroBuild Digital Operations (within 30 minutes)
- **P2 Incidents**: Escalate to service manager within 1 hour
- **P3 Incidents**: Escalate to service manager within 4 business hours

### Communication Channels
- **Primary**: Service portal
- **Secondary**: Project support hotline
- **Emergency**: Emergency hotline for P1 incidents only

## Special Instructions
- Site connectivity issues affecting active construction operations are escalated ahead of office requests
- All project management changes require approval from the project management team
- Coordinate with site managers before making network changes at construction sites
- Document access during critical project phases receives priority handling