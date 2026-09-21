# Atlas Legal Partners - Client Operations Documentation

## Client Details
- **Company Name**: Atlas Legal Partners
- **Account ID**: ACC-1004
- **Industry**: Legal Services
- **Company Size**: Mid-Market
- **Primary Region**: UK
- **Timezone**: Europe/London
- **Business Unit**: Legal Practice Management & IT Services

## IT Environment
- **Cloud Provider**: Microsoft Azure (uk-south)
- **On-Premises**: Main office in London with 2 satellite offices (Manchester, Birmingham)
- **Infrastructure Type**: SaaS-focused with Microsoft 365 ecosystem

## Applications

### CaseMaster Pro
- **Description**: Document management system handling case files, legal documents, client correspondence, and matter management for 150+ lawyers
- **Type**: Legal Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, SharePoint integration

### Office365 Suite
- **Description**: Microsoft 365 environment including Exchange Online, Teams, OneDrive, and SharePoint for collaboration and communication
- **Type**: Productivity Suite
- **Criticality**: Critical
- **Technology Stack**: Microsoft 365, Exchange Online, SharePoint Online

### LegalVault Secure
- **Description**: Secure document storage and archiving system with client privilege protection, version control, and retention policies
- **Type**: Document Management
- **Criticality**: High
- **Technology Stack**: Azure Blob Storage, Azure Key Vault, encryption at rest

### RemoteAccess Gateway
- **Description**: VPN and remote desktop infrastructure enabling secure remote access for lawyers working from home or client sites
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Azure VPN Gateway, Windows Server RDS, Duo Security

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for web applications
- **Secondary**: Internal load balancing for VPN infrastructure
- **Configuration**: Geo-redundant setup with automatic failover

### Identity & Access Management
- **Provider**: Azure Active Directory with conditional access policies
- **MFA**: Microsoft Authenticator with hardware token backup
- **Role-Based Access**: Practice group-based permissions with client matter access controls

### Servers
- **Application Servers**: 12x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (business-critical tier)
- **File Servers**: Azure Files with SMB protocol
- **Backup Servers**: Azure Backup with geo-redundant storage

### Firewalls & Security
- **Network Security**: Azure Firewall with application rules
- **Web Application Firewall**: Azure WAF for web applications
- **Network Segmentation**: Separate subnets for legal documents, general use, and guest access
- **Compliance**: SRA-regulated with ISO 27001 alignment

## Architecture & Dependencies

### Application Connectivity
- **CaseMaster Pro** ↔ **LegalVault Secure** ↔ Document storage and archiving
- **CaseMaster Pro** ↔ **Office365 Suite** ↔ Email integration and collaboration
- **RemoteAccess Gateway** ↔ All applications ↔ Secure remote access
- **All systems** ↔ Azure services (logging, monitoring, storage)

### Critical Dependencies
- **Office365 Suite** is required for daily communication and collaboration
- **CaseMaster Pro** depends on LegalVault Secure for document storage
- **RemoteAccess Gateway** is required for remote lawyer access
- **Internet connectivity with low latency for video conferencing**

### Data Flow
- Legal documents → CaseMaster Pro → LegalVault Secure → Secure storage
- Email/collaboration → Office365 Suite → Exchange Online/SharePoint
- Remote access → RemoteAccess Gateway → Internal applications

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with Application Insights
- **Microsoft 365**: Microsoft 365 Admin Center monitoring
- **Application Performance**: Custom monitoring for CaseMaster Pro
- **Security Monitoring**: Azure Sentinel with legal compliance rules

### Key Alerts
- **P1**: Firm-wide Office365 outage, CaseMaster Pro unavailable, VPN down
- **P2**: Multiple lawyers unable to access case systems, email delays, slow VPN performance
- **P3**: Individual user access issues, backup job failures, storage capacity warnings

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 7 years for legal compliance (SRA requirements)
- **Access Logs**: All document access logged for audit purposes

## Escalations

### Primary Contacts
- **Service Manager**: Oliver Grant (Client Service Manager)
- **Customer IT Owner**: Hannah Williams
- **Escalation Group**: Atlas Technology Committee

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Atlas Technology Committee (within 30 minutes)
- **P2 Incidents**: Escalate to service manager within 1 hour
- **P3 Incidents**: Escalate to service manager within 4 business hours

### Communication Channels
- **Primary**: Service portal
- **Secondary**: Email
- **Emergency**: Emergency hotline for P1 incidents only

## Special Instructions
- Do not access or modify client matter files unless explicitly authorized
- Security incidents involving privileged legal documents require immediate escalation
- All changes to legal systems require approval from the technology committee
- Follow SRA compliance procedures for data handling and privacy