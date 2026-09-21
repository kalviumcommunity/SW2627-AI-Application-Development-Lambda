# Pioneer University - Client Operations Documentation

## Client Details
- **Company Name**: Pioneer University
- **Account ID**: ACC-1012
- **Industry**: Education
- **Company Size**: Enterprise
- **Primary Region**: US
- **Timezone**: America/New_York
- **Business Unit**: Academic Operations & IT Services

## IT Environment
- **Cloud Provider**: Microsoft Azure (eastus)
- **On-Premises**: Main campus with 3 satellite locations and high-performance academic infrastructure
- **Infrastructure Type**: Education-focused with high availability for academic calendar

## Applications

### StudentHub SIS
- **Description**: Student Information System handling enrollment, grades, financial aid, course registration, and academic records for 50,000+ students
- **Type**: Academic Application
- **Criticality**: Critical
- **Technology Stack**: PeopleSoft, Oracle Database, SOAP APIs, student portal integration

### LearnSphere LMS
- **Description**: Learning Management System managing course content, assignments, discussions, assessments, and online learning for 3,000+ courses
- **Type**: Educational Application
- **Criticality**: Critical
- **Technology Stack**: Canvas LMS, PostgreSQL, LTI integration, video streaming

### CampusNet Core
- **Description**: Campus network infrastructure providing wired and wireless connectivity across all buildings, dormitories, and academic spaces
- **Type**: Network Application
- **Criticality**: Critical
- **Technology Stack**: Cisco DNA Center, Aruba wireless, network access control

### UniAuth Identity
- **Description**: Identity management system handling single sign-on, student/faculty authentication, and access control for all university systems
- **Type**: Security Application
- **Criticality**: Critical
- **Technology Stack**: Microsoft Azure AD, Shibboleth, LDAP, SAML 2.0

## Infrastructure

### Load Balancers
- **Primary**: Azure Application Gateway for web applications
- **Secondary**: Hardware load balancers on campus network
- **Configuration**: High-capacity configuration for peak academic periods

### Identity & Access Management
- **Provider**: Microsoft Azure Active Directory with education-specific policies
- **MFA**: Microsoft Authenticator for faculty and staff
- **Role-Based Access**: Role-based permissions with student/faculty/staff separation

### Servers
- **Application Servers**: 40x Azure Virtual Machines (D4s v3)
- **Database Servers**: Azure SQL Database (geo-replicated)
- **Campus Servers**: Dell PowerEdge for critical on-premises systems
- **Cache Servers**: Azure Cache for Redis

### Firewalls & Security
- **Network Security**: Azure Firewall with education-specific rules
- **Network Security**: Palo Alto firewalls on campus network
- **Network Segmentation**: Separate subnets for academic, administrative, and residential networks
- **Compliance**: FERPA compliance, EDUCAUSE guidelines

## Architecture & Dependencies

### Application Connectivity
- **StudentHub SIS** ↔ **LearnSphere LMS** ↔ Student enrollment and course data
- **StudentHub SIS** ↔ **UniAuth Identity** ↔ Student authentication
- **LearnSphere LMS** ↔ **CampusNet Core** ↔ Online learning access
- **All systems** ↔ Azure services (logging, monitoring, storage)

### Critical Dependencies
- **StudentHub SIS** is required for all student operations
- **LearnSphere LMS** is required for online learning and course delivery
- **UniAuth Identity** is required for access to all university systems
- **Campus network connectivity** for all academic and residential activities

### Data Flow
- Student data → StudentHub SIS → LearnSphere LMS → Course enrollment
- Learning activities → LearnSphere LMS → StudentHub SIS → Grade recording
- User access → UniAuth Identity → Application authorization

## Monitoring & Observability

### Monitoring Services
- **Infrastructure**: Azure Monitor with custom education metrics
- **Campus Monitoring**: Custom monitoring for campus network and systems
- **Application Performance**: AppDynamics APM for educational applications
- **Network Monitoring**: Cisco network monitoring for campus infrastructure

### Key Alerts
- **P1**: SIS system down, LMS unavailable during exams, campus network outage
- **P2**: Slow LMS performance, authentication delays, network congestion
- **P3**: Individual application errors, backup job failures, department-specific issues

### Log Management
- **Centralized Logging**: Azure Monitor Logs with Log Analytics
- **Retention**: 7 years for FERPA compliance
- **Access Logs**: All student data access logged for audit purposes

## Escalations

### Primary Contacts
- **Service Manager**: Robert Evans (Education Account Manager)
- **Customer IT Owner**: Maria Gonzalez
- **Escalation Group**: Pioneer University IT Operations

### Escalation Matrix
- **P1 Incidents**: Immediate escalation to Pioneer University IT Operations (within 15 minutes)
- **P2 Incidents**: Escalate to service manager within 30 minutes
- **P3 Incidents**: Escalate to service manager within 2 hours

### Communication Channels
- **Primary**: University IT portal
- **Secondary**: IT hotline
- **Emergency**: Direct escalation to CIO for academic-critical incidents

## Special Instructions
- During examination periods, LMS and identity incidents are automatically treated as P1
- All SIS changes require approval from the registrar's office
- Coordinate with academic calendar before making system changes during critical periods
- FERPA compliance procedures must be followed for all student data handling