# Oakridge Manufacturing - Client Operations Documentation

## Client Details
- **Company Name**: Oakridge Manufacturing
- **Account ID**: ACC-1008
- **Industry**: Manufacturing
- **Company Size**: Large
- **Primary Region**: Germany
- **Timezone**: Europe/Berlin
- **Business Unit**: Plant Operations & IT Infrastructure

## IT Environment
- **Cloud Provider**: Microsoft Azure (germany-westcentral)
- **On-Premises**: 8 manufacturing plants across Germany with OT/IT infrastructure
- **Infrastructure Type**: OT/IT convergence with IEC 62443 compliance

## Applications

### ProdTrack MES
- **Description**: Manufacturing Execution System managing production scheduling, quality control, work-in-progress tracking, and equipment integration across 8 plants
- **Type**: OT Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, OPC UA, Siemens PLC integration

### ERP Connect Core
- **Description**: Enterprise Resource Planning system handling supply chain, finance, HR, and inventory management with MES integration
- **Type**: Business Application
- **Criticality**: Critical
- **Technology Stack**: SAP S/4HANA, Oracle Database, IDoc interfaces

### PlantNet Manager
- **Description**: Network management system for plant infrastructure including industrial Ethernet, PLC networks, and plant-wide connectivity
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Cisco Industrial Network Director, Python, SNMP

### QualityView Dashboard
- **Description**: Real-time production monitoring dashboard providing visibility into quality metrics, equipment status, and production KPIs
- **Type**: Operations Application
- **Criticality**: High
- **Technology Stack**: React, Node.js, InfluxDB, Grafana

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for business applications
- **Secondary**: Industrial load balancers for plant networks
- **Configuration**: Plant-level failover with local redundancy

### Identity & Access Management
- **Provider**: Microsoft Active Directory with IEC 62443-compliant policies
- **MFA**: Hardware tokens for plant operators
- **Role-Based Access**: Strict separation between OT and IT environments

### Servers
- **Application Servers**: 28x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (geo-replicated)
- **Plant Servers**: Industrial PCs at each manufacturing location
- **OT Servers**: Siemens Industrial Edge servers in production areas

### Firewalls & Security
- **Network Security**: Azure Firewall with manufacturing-specific rules
- **Industrial Security**: Moxa industrial firewalls for OT network segmentation
- **Network Segmentation**: Complete separation between IT and OT networks with DMZ
- **Compliance**: IEC 62443, ISO 27001, German manufacturing standards

## Architecture & Dependencies

### Application Connectivity
- **ProdTrack MES** ↔ **ERP Connect Core** ↔ Production and business data sync
- **ProdTrack MES** ↔ **QualityView Dashboard** ↔ Real-time monitoring
- **PlantNet Manager** ↔ All systems ↔ Plant network infrastructure
- **OT systems** ↔ **IT systems** via secure DMZ with one-way data flow

### Critical Dependencies
- **ProdTrack MES** is required for all production operations
- **ERP Connect Core** is required for supply chain and business operations
- **PlantNet Manager** is required for plant network connectivity
- **OT-IT integration** via secure data diodes

### Data Flow
- Production data → ProdTrack MES → ERP Connect Core → Business systems
- Quality data → QualityView Dashboard → Management oversight
- Plant networks → PlantNet Manager → Infrastructure management

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with custom manufacturing metrics
- **OT Monitoring**: Custom SCADA monitoring with alarming
- **Application Performance**: AppDynamics APM for IT applications
- **Equipment Monitoring**: Siemens monitoring integration

### Key Alerts
- **P1**: MES outage stopping production, ERP system down, plant network failure
- **P2**: Production monitoring degradation, ERP sync issues, network performance problems
- **P3**: Individual application errors, backup job failures, non-critical system issues

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 10 years for manufacturing compliance
- **OT Logs**: Separate logging system with physical security

## Escalations

### Primary Contacts
- **Service Manager**: Anna Keller (Plant Technology Manager)
- **Customer IT Owner**: Lukas Weber
- **Escalation Group**: Oakridge Plant Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Oakridge Plant Operations (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Plant IT hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to Plant Director for production-critical incidents

## Special Instructions
- Do not reboot industrial controllers
- Coordinate all plant network changes with the local OT engineer
- All MES changes require approval from the production engineering team
- Follow IEC 62443 compliance procedures for OT system changes