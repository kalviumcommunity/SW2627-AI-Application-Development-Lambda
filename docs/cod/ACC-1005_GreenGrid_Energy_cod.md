# GreenGrid Energy - Client Operations Documentation

## Client Details
- **Company Name**: GreenGrid Energy
- **Account ID**: ACC-1005
- **Industry**: Energy & Utilities
- **Company Size**: Enterprise
- **Primary Region**: Canada
- **Timezone**: America/Toronto
- **Business Unit**: Grid Operations & Infrastructure Management

## IT Environment
- **Cloud Provider**: AWS (ca-central-1)
- **On-Premises**: 4 data centers supporting critical infrastructure across Ontario and Quebec
- **Infrastructure Type**: OT/IT convergence with NERC CIP compliance

## Applications

### GridWatch Core
- **Description**: Real-time grid monitoring system processing 100K+ telemetry points from substations, transmission lines, and distribution networks
- **Type**: Operational Technology Application
- **Criticality**: Critical
- **Technology Stack**: C++, PostgreSQL, DNP3 protocol, MQTT

### SCADA Support Hub
- **Description**: Supervisory Control and Data Acquisition support interface for operators to monitor and control grid equipment remotely
- **Type**: OT Application
- **Criticality**: Critical
- **Technology Stack**: Java, Oracle Database, OPC UA, Modbus

### NOC Command Center
- **Description**: Network Operations Center dashboard providing unified view of grid status, incident management, and operator workflows
- **Type**: Operations Application
- **Criticality**: High
- **Technology Stack**: React, Node.js, WebSocket, TimescaleDB

### CustomerBilling Pro
- **Description**: Billing and customer management system processing 2M+ customer accounts with smart meter data integration
- **Type**: Business Application
- **Criticality**: High
- **Technology Stack**: .NET, SQL Server, AMQP integration

## Infrastructure

### Load Balancers
- **Primary**: AWS Network Load Balancers for OT applications
- **Secondary**: Hardware load balancers for internal data center traffic
- **Configuration**: Active-passive setup with sub-second failover

### Identity & Access Management
- **Provider**: Microsoft Active Directory with NERC CIP-compliant policies
- **MFA**: YubiKey hardware tokens for OT operators
- **Role-Based Access**: Strict separation between IT and OT environments

### Servers
- **Application Servers**: 36x AWS EC2 instances (c5.2xlarge) in isolated VPCs
- **Database Servers**: Amazon RDS for PostgreSQL with Multi-AZ
- **OT Servers**: Dell PowerEdge in data centers with air-gapped networks
- **Cache Servers**: Amazon ElastiCache for Redis

### Firewalls & Security
- **Network Security**: Palo Alto Firewalls with OT-specific rules
- **Industrial Security**: Tofino firewalls for OT network segmentation
- **Network Segmentation**: Complete separation between IT and OT networks with data diodes
- **Compliance**: NERC CIP v5, ISO 27001, CSA critical infrastructure

## Architecture & Dependencies

### Application Connectivity
- **GridWatch Core** ↔ **SCADA Support Hub** ↔ Real-time control and monitoring
- **GridWatch Core** ↔ **NOC Command Center** ↔ Operator dashboards
- **CustomerBilling Pro** ↔ Smart meter data → Billing processing
- **OT systems** ↔ **IT systems** via secure data diodes (one-way communication)

### Critical Dependencies
- **GridWatch Core** is required for real-time grid monitoring
- **SCADA Support Hub** is required for remote equipment control
- **NOC Command Center** provides the primary operator interface
- **OT-IT data diodes** for secure one-way data flow

### Data Flow
- Grid telemetry → GridWatch Core → NOC Command Center → Operators
- Control commands → SCADA Support Hub → Grid equipment
- Meter data → CustomerBilling Pro → Billing processing

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: AWS CloudWatch with custom OT metrics
- **OT Monitoring**: Custom SCADA monitoring with alarming
- **Application Performance**: AppDynamics APM for IT applications
- **Security Monitoring**: AWS Security Hub with NERC CIP rules

### Key Alerts
- **P1**: Grid monitoring system failure, SCADA communication loss, data center outage
- **P2**: High latency in telemetry data, degraded operator dashboard performance, backup system issues
- **P3**: Individual application errors, storage capacity warnings, non-critical system degradations

### Log Management
- **Centralized Logging**: AWS CloudWatch Logs with S3 archive
- **Retention**: 10 years for NERC CIP compliance
- **OT Logs**: Separate logging system with physical security

## Escalations

### Primary Contacts
- **Service Manager**: Mark Thompson (Infrastructure Service Manager)
- **Customer IT Owner**: Aisha Patel
- **Escalation Group**: GreenGrid NOC

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to GreenGrid NOC leadership (within 10 minutes)
- **P2 Incidents**: Escalate to service manager within 20 minutes
- **P3 Incidents**: Escalate to service manager within 1 hour

### Communication Channels
- **Primary**: NOC hotline (24x7)
- **Secondary**: Service portal
- **Emergency**: Direct escalation to VP of Operations for grid emergencies

## Special Instructions
- Never directly modify operational control systems without customer authorization
- Operational technology incidents require NOC escalation
- All OT system changes require approval from the OT engineering team
- Follow NERC CIP compliance procedures for all infrastructure changes