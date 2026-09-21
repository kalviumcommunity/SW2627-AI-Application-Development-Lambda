# Nimbus Media Studios - Client Operations Documentation

## Client Details
- **Company Name**: Nimbus Media Studios
- **Account ID**: ACC-1007
- **Industry**: Media & Entertainment
- **Company Size**: Mid-Market
- **Primary Region**: US
- **Timezone**: America/Los_Angeles
- **Business Unit**: Production & Post-Production Services

## IT Environment
- **Cloud Provider**: Google Cloud Platform (us-west1)
- **On-Premises**: 3 studio locations in Los Angeles with production infrastructure
- **Infrastructure Type**: High-performance computing for media processing

## Applications

### MediaVault Pro
- **Description**: Media Asset Management system handling 50PB+ of video, audio, and image assets with metadata indexing and version control
- **Type**: Media Application
- **Criticality**: Critical
- **Technology Stack**: Python, PostgreSQL, Elasticsearch, object storage

### RenderForce Cluster
- **Description**: High-performance rendering cluster for 3D animation, visual effects, and video processing with GPU acceleration
- **Type**: Production Application
- **Criticality**: Critical
- **Technology Stack**: CUDA, OpenCL, custom rendering software, Kubernetes

### StudioNet Manager
- **Description**: Network management system for studio infrastructure including 10GbE production networks and storage area networks
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Cisco DNA Center, Python, SNMP

### Production Desk
- **Description**: Project management and workflow tracking system for production teams handling scheduling, resource allocation, and deliverable tracking
- **Type**: Business Application
- **Criticality**: High
- **Technology Stack**: React, Node.js, MongoDB, GraphQL

## Infrastructure

### Load Balancers
- **Primary**: Google Cloud Load Balancing for web applications
- **Secondary**: Hardware load balancers for studio networks
- **Configuration**: Content-aware routing with bandwidth optimization

### Identity & Access Management
- **Provider**: Google Workspace with studio-specific policies
- **MFA**: Google Authenticator with hardware token backup
- **Role-Based Access**: Project-based permissions with creative team access controls

### Servers
- **Application Servers**: 24x Google Compute Engine (c2-standard-60) with GPU
- **Database Servers**: Cloud SQL for PostgreSQL (high availability)
- **Storage Servers**: Google Cloud Storage with Nearline and Archive tiers
- **Render Nodes**: Custom GPU clusters in studio locations

### Firewalls & Security
- **Network Security**: Google Cloud Armor with media-specific rules
- **Network Security**: Fortinet firewalls at studio locations
- **Network Segmentation**: Separate subnets for production, post-production, and general use
- **Compliance**: MPAA content security guidelines

## Architecture & Dependencies

### Application Connectivity
- **MediaVault Pro** ↔ **RenderForce Cluster** ↔ Asset access for rendering
- **MediaVault Pro** ↔ **Production Desk** ↔ Project asset management
- **StudioNet Manager** ↔ All systems ↔ Network infrastructure management
- **All systems** ↔ Google Cloud services (logging, monitoring, storage)

### Critical Dependencies
- **MediaVault Pro** is required for all media asset access
- **RenderForce Cluster** is required for production rendering workflows
- **StudioNet Manager** is required for high-bandwidth studio networks
- **High-speed storage networks** for media file transfers

### Data Flow
- Production assets → MediaVault Pro → RenderForce Cluster → Finished content
- Project workflows → Production Desk → Resource allocation
- Network traffic → StudioNet Manager → Infrastructure management

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Google Cloud Monitoring with custom media metrics
- **Studio Monitoring**: Custom monitoring for production networks
- **Application Performance**: New Relic APM for business applications
- **Storage Monitoring**: Custom storage capacity and performance monitoring

### Key Alerts
- **P1**: Production storage unavailable, rendering cluster down, studio network failure
- **P2**: Slow rendering performance, storage capacity critical, network degradation
- **P3**: Individual application errors, backup job failures, workstation issues

### Log Management
- **Centralized Logging**: Google Cloud Logging with export to BigQuery
- **Retention**: 5 years for project assets, 1 year for application logs
- **Studio Logs**: Real-time monitoring during active production

## Escalations

### Primary Contacts
- **Service Manager**: Rachel Kim (Media Technology Manager)
- **Customer IT Owner**: Tom Wilson
- **Escalation Group**: Nimbus Production Engineering

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Nimbus Production Engineering (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Production hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to CTO for production-critical incidents

## Special Instructions
- Never delete media assets as part of incident remediation
- Production incidents during live shoots receive P1 priority
- All storage changes require approval from the media engineering team
- Coordinate with production teams before making infrastructure changes during active shoots