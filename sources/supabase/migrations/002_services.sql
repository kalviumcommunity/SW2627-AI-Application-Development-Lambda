CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


INSERT INTO services (client_id, service_name) VALUES
-- ACC-1001: Northstar Health Systems
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Managed Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Service Desk'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Security Monitoring'),

-- ACC-1002: VertexPay Financial
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Cloud Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Database Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Application Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Security Operations'),

-- ACC-1003: BluePeak Retail Group
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Store Network Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Cloud Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'POS Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Service Desk'),

-- ACC-1004: Atlas Legal Partners
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Microsoft 365'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Endpoint Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Identity Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Service Desk'),

-- ACC-1005: GreenGrid Energy
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Infrastructure Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Network Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), '24x7 Monitoring'),

-- ACC-1006: Crestline Logistics
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Warehouse Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Network Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Service Desk'),

-- ACC-1007: Nimbus Media Studios
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Cloud Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Media Storage'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Workstation Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Network Operations'),

-- ACC-1008: Oakridge Manufacturing
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Plant IT'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Network Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Endpoint Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'ERP Support'),

-- ACC-1009: HarborView Hotels
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Property Network'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Guest Wi-Fi'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Cloud Applications'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Service Desk'),

-- ACC-1010: Summit Biotech
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Research Computing'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Cloud Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Identity Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Security Monitoring'),

-- ACC-1011: MetroBuild Construction
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Field Connectivity'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Microsoft 365'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Service Desk'),

-- ACC-1012: Pioneer University
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Campus Network'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Identity Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Service Desk'),

-- ACC-1013: SilverOak Insurance
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Application Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Cloud Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Database Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Security Operations'),

-- ACC-1014: Redwood Aerospace
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Infrastructure Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Network Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Endpoint Management'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Security Operations'),

-- ACC-1015: Coastal Foods International
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'ERP Support'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Plant Infrastructure'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Cloud Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Service Desk');