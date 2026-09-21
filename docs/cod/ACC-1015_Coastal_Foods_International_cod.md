# Coastal Foods International - Client Operations Documentation

## Client Details
- **Company Name**: Coastal Foods International
- **Account ID**: ACC-1015
- **Industry**: Food & Beverage
- **Company Size**: Large
- **Primary Region**: India
- **Timezone**: Asia/Kolkata
- **Business Unit**: Manufacturing Operations & Supply Chain

## IT Environment
- **Cloud Provider**: Microsoft Azure (south-india)
- **On-Premises**: 8 manufacturing plants and 4 distribution centers across India
- **Infrastructure Type**: Manufacturing-focused with food safety compliance (FSSAI, HACCP)

## Applications

### FoodPro ERP
- **Description**: Enterprise Resource Planning system handling production planning, inventory management, finance, HR, and supply chain operations for food manufacturing
- **Type**: Business Application
- **Criticality**: Critical
- **Technology Stack**: SAP S/4HANA, SQL Server, integration with manufacturing systems

### WarehouseFlow WMS
- **Description**: Warehouse Management System managing inventory, picking, packing, shipping, and distribution across 4 distribution centers
- **Type**: Logistics Application
- **Criticality**: Critical
- **Technology Stack**: Java, Oracle Database, barcode scanning, IoT sensors

### ProductionTrack MES
- **Description**: Manufacturing Execution System managing production scheduling, quality control, batch tracking, and equipment integration for food processing
- **Type**: Manufacturing Application
- **Criticality**: High
- **Technology Stack**: .NET, SQL Server, PLC integration, HACCP compliance

### PlantNet Manager
- **Description**: Network management system for plant infrastructure including industrial networks, connectivity between plants and distribution centers
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Cisco Industrial Network Director, Python, SNMP

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for business applications
- **Secondary**: Hardware load balancers at plants and distribution centers
- **Configuration**: Geographic routing with plant-level failover

### Identity & Access Management
- **Provider**: Microsoft Azure Active Directory with manufacturing-specific policies
- **MFA**: Microsoft Authenticator for plant managers
- **Role-Based Access**: Plant-based permissions with regional management capabilities

### Servers
- **Application Servers**: 32x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (geo-replicated)
- **Plant Servers**: Dell PowerEdge at manufacturing locations
- **Distribution Center Servers**: Ruggedized servers at distribution centers

### Firewalls & Security
- **Network Security**: Azure Firewall with food industry-specific rules
- **Network Security**: Fortinet firewalls at plants and distribution centers
- **Network Segmentation**: Separate subnets for production, warehousing, and corporate systems
- **Compliance**: FSSAI compliance, HACCP, ISO 22000, food safety standards

## Architecture & Dependencies

### Application Connectivity
- **FoodPro ERP** ↔ **WarehouseFlow WMS** ↔ Inventory and distribution integration
- **FoodPro ERP** ↔ **ProductionTrack MES** ↔ Production planning and execution
- **WarehouseFlow WMS** ↔ **PlantNet Manager** ↔ Distribution network connectivity
- **All systems** ↔ Azure services (logging, monitoring, storage)

### Critical Dependencies
- **FoodPro ERP** is required for all business operations
- **WarehouseFlow WMS** is required for distribution and inventory management
- **ProductionTrack MES** is required for manufacturing operations
- **Plant and distribution center connectivity via MPLS**

### Data Flow
- Production data → ProductionTrack MES → FoodPro ERP → Business systems
- Inventory data → WarehouseFlow WMS → FoodPro ERP → Supply chain
- Distribution operations → WarehouseFlow WMS → PlantNet Manager → Network management

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with custom food industry metrics
- **Plant Monitoring**: Custom monitoring for manufacturing equipment
- **Application Performance**: AppDynamics APM for business applications
- **Network Monitoring**: Cisco SD-WAN monitoring

### Key Alerts
- **P1**: ERP system down, WMS outage halting distribution, production system failure
- **P2**: Inventory sync issues, production scheduling problems, network connectivity degradation
- **P3**: Individual application errors, backup job failures, plant-specific issues

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 5 years for food safety compliance
- **Access Logs**: All production and inventory data access logged

## Escalations

### Primary Contacts
- **Service Manager**: Ravi Menon (India Account Manager)
- **Customer IT Owner**: Neha Kapoor
- **Escalation Group**: Coastal Foods IT Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Coastal Foods IT Operations (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Service desk hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to VP of Operations for production-critical incidents

## Special Instructions
- Production-impacting ERP incidents are P1 regardless of number of affected users
- Plant changes require approval from the local IT lead
- All MES changes require approval from the production engineering team
- Follow food safety compliance procedures for all system changes affecting production