# Redwood Aerospace - Client Operations Documentation

## Client Details
- **Company Name**: Redwood Aerospace
- **Account ID**: ACC-1014
- **Industry**: Aerospace & Defense
- **Company Size**: Enterprise
- **Primary Region**: US
- **Timezone**: America/Los_Angeles
- **Business Unit**: Engineering & Manufacturing Operations

## IT Environment
- **Cloud Provider**: AWS (us-gov-west-1) - GovCloud
- **On-Premises**: 4 secure facilities with classified computing infrastructure
- **Infrastructure Type**: Defense-focused with ITAR/EAR compliance and security clearance requirements

## Applications

### AeroDesign Suite
- **Description**: Engineering systems platform handling CAD/CAM/CAE applications, product lifecycle management, and engineering collaboration for aerospace design
- **Type**: Engineering Application
- **Criticality**: Critical
- **Technology Stack**: Siemens Teamcenter, NX CAD, ANSYS simulation, high-performance computing

### ManufacturTrack MES
- **Description**: Manufacturing Execution System managing production scheduling, quality control, and assembly operations for aerospace components
- **Type**: Manufacturing Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, PLC integration, aerospace quality standards

### SecureFile Vault
- **Description**: Secure file transfer and storage system for classified technical data, engineering drawings, and controlled documents with encryption and access controls
- **Type**: Security Application
- **Criticality**: Critical
- **Technology Stack**: custom encryption, PKI, air-gapped storage, audit logging

### ClearAuth Identity
- **Description**: Identity management system with security clearance verification, role-based access control, and audit trails for defense contractor operations
- **Type**: Security Application
- **Criticality**: Critical
- **Technology Stack**: Microsoft Active Directory with defense extensions, smart card integration

## Infrastructure

### Load Balancers
- **Primary**: AWS Network Load Balancers for approved applications
- **Secondary**: Hardware load balancers in secure facilities
- **Configuration**: High-security configuration with strict access controls

### Identity & Access Management
- **Provider**: Microsoft Active Directory with defense-specific policies
- **MFA**: CAC/PIV smart cards for all personnel
- **Role-Based Access**: Clearance-based permissions with need-to-know controls

### Servers
- **Application Servers**: 24x AWS EC2 instances (GovCloud compliant)
- **Database Servers**: Amazon RDS for SQL Server (GovCloud)
- **Secure Facility Servers**: Dell PowerEdge in classified environments
- **HPC Clusters**: Custom high-performance computing for engineering

### Firewalls & Security
- **Network Security**: AWS GovCloud Firewall with defense-specific rules
- **Network Security**: Palo Alto firewalls with defense compliance
- **Network Segmentation**: Complete separation between classified and unclassified networks
- **Compliance**: ITAR, EAR, DFARS, CMMC Level 3, NIST 800-171

## Architecture & Dependencies

### Application Connectivity
- **AeroDesign Suite** ↔ **ManufacturTrack MES** ↔ Engineering to manufacturing handoff
- **AeroDesign Suite** ↔ **SecureFile Vault** ↔ Secure engineering data storage
- **ManufacturTrack MES** ↔ **ClearAuth Identity** ↔ Manufacturing access control
- **Classified systems** ↔ **Unclassified systems** via data diodes (one-way only)

### Critical Dependencies
- **AeroDesign Suite** is required for all engineering operations
- **ManufacturTrack MES** is required for manufacturing operations
- **SecureFile Vault** is required for classified data handling
- **Cross-domain solutions** for secure data transfer between classification levels

### Data Flow
- Engineering data → AeroDesign Suite → SecureFile Vault → Classified storage
- Manufacturing data → ManufacturTrack MES → Quality control systems
- User access → ClearAuth Identity → Application authorization

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: AWS CloudWatch with GovCloud compliance
- **Security Monitoring**: Custom security monitoring with defense compliance rules
- **Application Performance**: AppDynamics APM for engineering applications
- **Facility Monitoring**: Custom monitoring for secure facility infrastructure

### Key Alerts
- **P1**: Engineering systems down, manufacturing system unavailable, security breach detected
- **P2**: Engineering performance degradation, manufacturing sync issues, access control problems
- **P3**: Individual application errors, backup job failures, non-critical system issues

### Log Management
- **Centralized Logging**: AWS CloudWatch Logs with GovCloud compliance
- **Retention**: 10 years for defense compliance requirements
- **Access Logs**: All classified data access logged for security audits

## Escalations

### Primary Contacts
- **Service Manager**: Eric Johnson (Defense Account Manager)
- **Customer IT Owner**: Rachel Adams
- **Escalation Group**: Redwood Security Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Redwood Security Operations (within 10 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Secure service portal
- **Secondary**: Operations hotline
- **Emergency**: Direct escalation to CISO for security incidents

## Special Instructions
- Do not transfer restricted data to non-approved systems
- Security incidents must follow the customer security incident response process
- All engineering system changes require approval from the engineering team
- Follow ITAR/EAR compliance procedures for all technical data handling