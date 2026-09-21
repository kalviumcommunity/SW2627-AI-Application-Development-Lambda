# Summit Biotech - Client Operations Documentation

## Client Details
- **Company Name**: Summit Biotech
- **Account ID**: ACC-1010
- **Industry**: Biotechnology
- **Company Size**: Mid-Market
- **Primary Region**: US
- **Timezone**: America/New_York
- **Business Unit**: Research Computing & Laboratory Operations

## IT Environment
- **Cloud Provider**: Google Cloud Platform (us-east1)
- **On-Premises**: 3 research facilities with high-performance computing infrastructure
- **Infrastructure Type**: Research-focused with regulatory compliance (GLP/GMP)

## Applications

### LabTrack LIMS
- **Description**: Laboratory Information Management System handling sample tracking, experiment data, quality control, and regulatory compliance for biotech research
- **Type**: Research Application
- **Criticality**: Critical
- **Technology Stack**: Python, PostgreSQL, barcode scanning, instrument integration

### ResearchData Hub
- **Description**: Research data platform managing genomics data, experimental results, and scientific collaboration with 50PB+ storage
- **Type**: Data Platform
- **Criticality**: Critical
- **Technology Stack**: Hadoop, Spark, object storage, data lakes

### BioAuth Identity
- **Description**: Identity management system with role-based access control, audit logging, and compliance for regulated research environments
- **Type**: Security Application
- **Criticality**: Critical
- **Technology Stack**: Okta, LDAP, custom compliance policies

### CloudLab Storage
- **Description**: Cloud storage system for research data backup, archival, and sharing with encryption and access controls
- **Type**: Storage Application
- **Criticality**: High
- **Technology Stack**: Google Cloud Storage, Cloud KMS, custom access controls

## Infrastructure

### Load Balancers
- **Primary**: Google Cloud Load Balancing for web applications
- **Secondary**: Internal load balancing for research computing
- **Configuration**: High-throughput configuration for data-intensive workloads

### Identity & Access Management
- **Provider**: Okta with biotech-specific compliance policies
- **MFA**: YubiKey hardware tokens for research staff
- **Role-Based Access**: Experiment-based permissions with data classification controls

### Servers
- **Application Servers**: 20x Google Compute Engine (n2-highmem-32)
- **Database Servers**: Cloud SQL for PostgreSQL (high availability)
- **Compute Clusters**: Custom HPC clusters for genomics processing
- **Storage Servers**: Google Cloud Storage with custom tiers

### Firewalls & Security
- **Network Security**: Google Cloud Armor with research-specific rules
- **Network Security**: Palo Alto firewalls at research facilities
- **Network Segmentation**: Separate subnets for research, clinical, and administrative systems
- **Compliance**: GLP/GMP compliance, FDA 21 CFR Part 11, HIPAA

## Architecture & Dependencies

### Application Connectivity
- **LabTrack LIMS** ↔ **ResearchData Hub** ↔ Experiment data integration
- **LabTrack LIMS** ↔ **BioAuth Identity** ↔ Access control and compliance
- **ResearchData Hub** ↔ **CloudLab Storage** ↔ Data archival and backup
- **All systems** ↔ Google Cloud services (logging, monitoring, storage)

### Critical Dependencies
- **LabTrack LIMS** is required for all laboratory operations
- **ResearchData Hub** is required for research data processing
- **BioAuth Identity** is required for compliance and access control
- **High-speed network** for data-intensive research workflows

### Data Flow
- Laboratory data → LabTrack LIMS → ResearchData Hub → Analysis
- Research results → ResearchData Hub → CloudLab Storage → Archival
- User access → BioAuth Identity → Application authorization

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Google Cloud Monitoring with custom research metrics
- **Lab Monitoring**: Custom monitoring for laboratory instruments
- **Application Performance**: New Relic APM for research applications
- **Security Monitoring**: Google Cloud Security Command Center

### Key Alerts
- **P1**: LIMS system down, research data platform unavailable, identity system failure
- **P2**: Slow data processing, storage capacity critical, lab instrument integration issues
- **P3**: Individual application errors, backup job failures, non-critical system issues

### Log Management
- **Centralized Logging**: Google Cloud Logging with export to BigQuery
- **Retention**: 25 years for research compliance (FDA requirements)
- **Access Logs**: All data access logged for audit purposes

## Escalations

### Primary Contacts
- **Service Manager**: Laura Bennett (Research IT Manager)
- **Customer IT Owner**: Kevin Moore
- **Escalation Group**: Summit Security Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Summit Security Operations (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Research IT hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to CTO for research-critical incidents

## Special Instructions
- Do not delete research data during troubleshooting
- Suspected data exposure must immediately involve the security team
- All LIMS changes require approval from the research compliance team
- Follow GLP/GMP compliance procedures for all system changes