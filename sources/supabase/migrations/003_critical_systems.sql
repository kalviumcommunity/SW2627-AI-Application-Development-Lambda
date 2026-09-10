-- Critical systems table
CREATE TABLE critical_systems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    system_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert critical systems for each client
INSERT INTO critical_systems (client_id, system_name) VALUES
-- ACC-1001: Northstar Health Systems
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Electronic Health Records'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Clinical API Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Identity and Access Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Hospital Network'),

-- ACC-1002: VertexPay Financial
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Payment Gateway'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Transaction Processing Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Fraud Detection Engine'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Customer Authentication'),

-- ACC-1003: BluePeak Retail Group
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Point of Sale'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Store Network'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Inventory Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'E-commerce Platform'),

-- ACC-1004: Atlas Legal Partners
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Document Management System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Microsoft 365'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Email'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Remote Access VPN'),

-- ACC-1005: GreenGrid Energy
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Grid Monitoring'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'SCADA Support Systems'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Network Operations Center'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Customer Billing'),

-- ACC-1006: Crestline Logistics
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Warehouse Management System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Fleet Tracking'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'EDI Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Warehouse Wi-Fi'),

-- ACC-1007: Nimbus Media Studios
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Media Asset Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Production Storage'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Rendering Cluster'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Studio Network'),

-- ACC-1008: Oakridge Manufacturing
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Manufacturing Execution System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'ERP'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Plant Network'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Production Monitoring'),

-- ACC-1009: HarborView Hotels
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Property Management System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Guest Wi-Fi'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Booking Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Payment Terminals'),

-- ACC-1010: Summit Biotech
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Laboratory Information System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Research Data Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Identity Provider'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Cloud Storage'),

-- ACC-1011: MetroBuild Construction
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Project Management Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Document Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Field Connectivity'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Microsoft 365'),

-- ACC-1012: Pioneer University
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Student Information System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Learning Management System'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Campus Network'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Identity Provider'),

-- ACC-1013: SilverOak Insurance
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Claims Platform'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Policy Administration'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Customer Portal'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Identity Platform'),

-- ACC-1014: Redwood Aerospace
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Engineering Systems'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Manufacturing Systems'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Secure File Transfer'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Identity Management'),

-- ACC-1015: Coastal Foods International
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'ERP'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Warehouse Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Production Planning'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Distribution Network');
