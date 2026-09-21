# HarborView Hotels - Client Operations Documentation

## Client Details
- **Company Name**: HarborView Hotels
- **Account ID**: ACC-1009
- **Industry**: Hospitality
- **Company Size**: Enterprise
- **Primary Region**: Singapore
- **Timezone**: Asia/Singapore
- **Business Unit**: Hotel Operations & Guest Services

## IT Environment
- **Cloud Provider**: AWS (ap-southeast-1)
- **On-Premises**: 12 luxury hotel properties across Asia Pacific with local infrastructure
- **Infrastructure Type**: Hospitality-focused with guest experience applications

## Applications

### StayEase PMS
- **Description**: Property Management System handling reservations, check-in/check-out, housekeeping management, and guest services across 12 properties
- **Type**: Hospitality Application
- **Criticality**: Critical
- **Technology Stack**: .NET, SQL Server, SOAP APIs, PMS interface standards

### GuestConnect Wi-Fi
- **Description**: Guest Wi-Fi management system providing captive portal, bandwidth management, and personalized guest experiences
- **Type**: Network Application
- **Criticality**: Critical
- **Technology Stack**: Cisco DNA Center, RADIUS, custom captive portal

### ReservePro Booking
- **Description**: Central booking platform for online reservations, channel management, and rate synchronization with OTAs
- **Type**: Web Application
- **Criticality**: High
- **Technology Stack**: React, Node.js, PostgreSQL, Channel Manager APIs

### PayDesk Terminal
- **Description**: Payment processing system for front desk, restaurants, and spa services with EMV compliance and multi-currency support
- **Type**: Payment Application
- **Criticality**: High
- **Technology Stack**: Java, PCI-compliant payment gateway, EMV integration

## Infrastructure

### Load Balancers
- **Primary**: AWS Application Load Balancers for web applications
- **Secondary**: Hardware load balancers at hotel properties
- **Configuration**: Geographic routing with property-level failover

### Identity & Access Management
- **Provider**: Microsoft Azure Active Directory with hospitality policies
- **MFA**: Microsoft Authenticator for hotel staff
- **Role-Based Access**: Property-based permissions with regional management capabilities

### Servers
- **Application Servers**: 32x AWS EC2 instances (m5.xlarge)
- **Database Servers**: Amazon RDS for SQL Server with Multi-AZ
- **Property Servers**: Dell PowerEdge at each hotel location
- **Cache Servers**: Amazon ElastiCache for Redis

### Firewalls & Security
- **Network Security**: AWS WAF with hospitality-specific rules
- **Network Security**: Fortinet firewalls at hotel properties
- **Network Segmentation**: Separate subnets for guest Wi-Fi, back-office, and payment systems
- **Compliance**: PCI-DSS Level 1 for payment processing, local hospitality regulations

## Architecture & Dependencies

### Application Connectivity
- **StayEase PMS** ↔ **ReservePro Booking** ↔ Reservation synchronization
- **StayEase PMS** ↔ **PayDesk Terminal** ↔ Payment processing
- **GuestConnect Wi-Fi** ↔ Guest devices ↔ Internet access
- **All systems** ↔ AWS services (logging, monitoring, storage)

### Critical Dependencies
- **StayEase PMS** is required for all hotel operations
- **GuestConnect Wi-Fi** is required for guest internet access
- **PayDesk Terminal** is required for payment processing
- **Property connectivity via SD-WAN**

### Data Flow
- Guest reservations → ReservePro Booking → StayEase PMS → Property operations
- Payment transactions → PayDesk Terminal → Payment gateway
- Guest Wi-Fi → GuestConnect Wi-Fi → Internet access

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: AWS CloudWatch with custom hospitality metrics
- **Property Monitoring**: Custom agents at hotel locations
- **Application Performance**: Datadog APM for hospitality applications
- **Network Monitoring**: Cisco SD-WAN monitoring

### Key Alerts
- **P1**: PMS outage preventing check-in/check-out, guest Wi-Fi down, payment terminal failure
- **P2**: Slow booking system performance, Wi-Fi congestion, PMS sync issues
- **P3**: Individual application errors, backup job failures, property-specific issues

### Log Management
- **Centralized Logging**: AWS CloudWatch Logs with S3 archive
- **Retention**: 7 years for hospitality compliance
- **Property Logs**: Daily upload to central storage

## Escalations

### Primary Contacts
- **Service Manager**: Wei Tan (Hospitality Account Manager)
- **Customer IT Owner**: James Lim
- **Escalation Group**: HarborView Regional IT

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to HarborView Regional IT (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: Hotel operations hotline
- **Secondary**: Service portal
- **Emergency**: Direct escalation to VP of Operations for guest-facing emergencies

## Special Instructions
- Guest-facing outages take precedence over back-office issues
- Payment terminal incidents must be coordinated with hotel finance
- All PMS changes require approval from hotel operations team
- Coordinate with property management before making network changes during peak check-in times