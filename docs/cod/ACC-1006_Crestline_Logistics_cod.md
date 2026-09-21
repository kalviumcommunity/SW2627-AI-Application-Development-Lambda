# Crestline Logistics - Client Operations Documentation

## Client Details
- **Company Name**: Crestline Logistics
- **Account ID**: ACC-1006
- **Industry**: Transportation & Logistics
- **Company Size**: Large
- **Primary Region**: US
- **Timezone**: America/Denver
- **Business Unit**: Warehouse Operations & Fleet Management

## IT Environment
- **Cloud Provider**: AWS (us-west-2)
- **On-Premises**: 25 distribution centers across US with local infrastructure
- **Infrastructure Type**: Hybrid cloud with edge computing at warehouse locations

## Applications

### WarehouseCommand Pro
- **Description**: Warehouse Management System handling inventory, picking, packing, and shipping operations across 25 distribution centers
- **Type**: Logistics Application
- **Criticality**: Critical
- **Technology Stack**: Java, Oracle Database, barcode scanning integration

### FleetTrack GPS
- **Description**: Real-time fleet tracking system monitoring 500+ trucks with GPS, route optimization, and driver communication
- **Type**: Fleet Management Application
- **Criticality**: Critical
- **Technology Stack**: .NET, PostgreSQL, GPS/telematics integration

### EDI Connect Hub
- **Description**: Electronic Data Interchange platform handling B2B transactions with suppliers, retailers, and trading partners
- **Type**: Integration Platform
- **Criticality**: High
- **Technology Stack**: MuleSoft, AS2/FTP protocols, XML/EDI processing

### Warehouse Wi-Fi Manager
- **Description**: Network management system for warehouse Wi-Fi infrastructure supporting handheld scanners and mobile devices
- **Type**: Network Application
- **Criticality**: High
- **Technology Stack**: Cisco DNA Center, Python, SNMP

## Infrastructure

### Load Balancers
- **Primary**: AWS Application Load Balancers for web applications
- **Secondary**: Hardware load balancers at warehouse locations
- **Configuration**: Geographic routing with regional failover

### Identity & Access Management
- **Provider**: Okta with warehouse-specific policies
- **MFA**: DUO Security for warehouse managers
- **Role-Based Access**: Location-based permissions with regional override capabilities

### Servers
- **Application Servers**: 40x AWS EC2 instances (m5.xlarge)
- **Database Servers**: Amazon RDS for Oracle with Multi-AZ
- **Warehouse Servers**: Dell PowerEdge at each distribution center
- **Cache Servers**: Amazon ElastiCache for Redis

### Firewalls & Security
- **Network Security**: AWS WAF with custom logistics rules
- **Network Security**: Cisco Firepower at warehouse locations
- **Network Segmentation**: Separate subnets for WMS, fleet tracking, and general use
- **Compliance**: TAPA security standards for logistics facilities

## Architecture & Dependencies

### Application Connectivity
- **WarehouseCommand Pro** ↔ **FleetTrack GPS** ↔ Shipping and pickup coordination
- **WarehouseCommand Pro** ↔ **EDI Connect Hub** ↔ Supply chain integration
- **Warehouse Wi-Fi Manager** ↔ Handheld devices ↔ Warehouse operations
- **All systems** ↔ AWS services (logging, monitoring, storage)

### Critical Dependencies
- **WarehouseCommand Pro** is required for all warehouse operations
- **FleetTrack GPS** is required for fleet management and logistics coordination
- **Warehouse Wi-Fi Manager** is required for handheld scanner connectivity
- **SD-WAN connectivity between warehouses and cloud**

### Data Flow
- Warehouse operations → WarehouseCommand Pro → Central inventory
- Fleet data → FleetTrack GPS → Route optimization
- Supply chain → EDI Connect Hub → WarehouseCommand Pro

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: AWS CloudWatch with custom logistics metrics
- **Warehouse Monitoring**: Custom agents at distribution centers
- **Application Performance**: Dynatrace APM for WMS and fleet tracking
- **Network Monitoring**: Cisco SD-WAN monitoring

### Key Alerts
- **P1**: WMS outage at multiple warehouses, fleet tracking system down, warehouse Wi-Fi failure
- **P2**: Single warehouse WMS outage, GPS tracking delays, Wi-Fi performance issues
- **P3**: Individual application errors, backup job failures, storage capacity warnings

### Log Management
- **Centralized Logging**: AWS CloudWatch Logs with S3 archive
- **Retention**: 5 years for logistics compliance
- **Warehouse Logs**: Daily upload to central storage

## Escalations

### Primary Contacts
- **Service Manager**: Daniel Brooks (Account Manager)
- **Customer IT Owner**: Carlos Martinez
- **Escalation Group**: Crestline Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Crestline Operations leadership
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Operations hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to VP of Operations for shipping-critical incidents

## Special Instructions
- Warehouse outages affecting shipping cutoffs must be treated as P1
- Coordinate with local warehouse management before restarting network equipment
- All WMS changes require approval from warehouse operations team
- Fleet tracking outages during peak shipping seasons receive priority handling