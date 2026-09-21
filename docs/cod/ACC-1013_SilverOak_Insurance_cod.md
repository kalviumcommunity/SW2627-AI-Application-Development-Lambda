# SilverOak Insurance - Client Operations Documentation

## Client Details
- **Company Name**: SilverOak Insurance
- **Account ID**: ACC-1013
- **Industry**: Insurance
- **Company Size**: Enterprise
- **Primary Region**: UK
- **Timezone**: Europe/London
- **Business Unit**: Insurance Operations & Customer Services

## IT Environment
- **Cloud Provider**: Microsoft Azure (uk-south)
- **On-Premises**: 2 data centers in UK with backup infrastructure
- **Infrastructure Type**: Insurance-focused with regulatory compliance (FCA, Solvency II)

## Applications

### ClaimFlow Pro
- **Description**: Claims processing platform handling auto, home, and commercial insurance claims with workflow automation, document management, and fraud detection
- **Type**: Insurance Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, document scanning integration, AI fraud detection

### PolicyMaster Core
- **Description**: Policy administration system managing policy issuance, renewals, endorsements, and customer data for 2M+ policyholders
- **Type**: Insurance Application
- **Criticality**: Critical
- **Technology Stack**: Java, Oracle Database, rule engine, CRM integration

### CustomerPortal Plus
- **Description**: Customer-facing web portal for policy management, claims submission, document upload, and self-service capabilities
- **Type**: Web Application
- **Criticality**: High
- **Technology Stack**: React, Node.js, GraphQL, PostgreSQL

### SecureAuth Gateway
- **Description**: Identity management platform with role-based access control, audit logging, and compliance for insurance operations
- **Type**: Security Application
- **Criticality**: Critical
- **Technology Stack**: Microsoft Azure AD, custom insurance policies, MFA

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for web applications
- **Secondary**: Hardware load balancers in data centers
- **Configuration**: High-availability setup with geographic failover

### Identity & Access Management
- **Provider**: Microsoft Azure Active Directory with insurance-specific policies
- **MFA**: Microsoft Authenticator with hardware token backup
- **Role-Based Access**: Department-based permissions with customer data access controls

### Servers
- **Application Servers**: 36x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (geo-replicated)
- **Data Center Servers**: Dell PowerEdge for critical on-premises systems
- **Cache Servers**: Azure Cache for Redis

### Firewalls & Security
- **Network Security**: Azure Firewall with insurance-specific rules
- **Network Security**: Check Point firewalls in data centers
- **Network Segmentation**: Separate subnets for claims, policy, and customer portal systems
- **Compliance**: FCA compliance, Solvency II, GDPR, ISO 27001

## Architecture & Dependencies

### Application Connectivity
- **ClaimFlow Pro** ↔ **PolicyMaster Core** ↔ Policy and claims data integration
- **ClaimFlow Pro** ↔ **CustomerPortal Plus** ↔ Customer claims submission
- **PolicyMaster Core** ↔ **SecureAuth Gateway** ↔ Access control and compliance
- **All systems** ↔ Azure services (logging, monitoring, storage)

### Critical Dependencies
- **ClaimFlow Pro** is required for all claims processing operations
- **PolicyMaster Core** is required for policy administration
- **SecureAuth Gateway** is required for compliance and access control
- **Database replication** for high availability and disaster recovery

### Data Flow
- Claims data → ClaimFlow Pro → PolicyMaster Core → Policy updates
- Customer actions → CustomerPortal Plus → ClaimFlow Pro/PolicyMaster Core
- User access → SecureAuth Gateway → Application authorization

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with custom insurance metrics
- **Application Performance**: AppDynamics APM for insurance applications
- **Business Monitoring**: Custom dashboards for claims processing metrics
- **Security Monitoring**: Azure Sentinel with insurance compliance rules

### Key Alerts
- **P1**: Claims processing system down, policy administration unavailable, customer portal failure
- **P2**: Slow claims processing, policy sync issues, authentication delays
- **P3**: Individual application errors, backup job failures, non-critical system issues

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 7 years for regulatory compliance (FCA requirements)
- **Access Logs**: All customer data access logged for audit purposes

## Escalations

### Primary Contacts
- **Service Manager**: George Wilson (Insurance Account Director)
- **Customer IT Owner**: Amelia Brown
- **Escalation Group**: SilverOak IT Leadership

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to SilverOak IT Leadership (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Service portal
- **Secondary**: Major incident hotline
- **Emergency**: Direct escalation to CIO for regulatory-critical incidents

## Special Instructions
- Regulatory reporting deadlines require priority escalation
- Security incidents must be coordinated with SilverOak Security Operations
- All claims system changes require approval from the claims management team
- Follow FCA compliance procedures for all customer data handling