-- Contacts table
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    service_manager VARCHAR(255),
    service_manager_role VARCHAR(255),
    customer_it_owner VARCHAR(255),
    escalation_group VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert contacts
INSERT INTO contacts (client_id, service_manager, service_manager_role, customer_it_owner, escalation_group) VALUES
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Sarah Mitchell', 'Account Service Manager', 'David Chen', 'Northstar IT Leadership'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Michael Torres', 'Financial Services Account Director', 'Priya Shah', 'VertexPay SRE Leadership'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Jason Lee', 'Retail Operations Manager', 'Emily Rodriguez', 'BluePeak Store Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Oliver Grant', 'Client Service Manager', 'Hannah Williams', 'Atlas Technology Committee'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Mark Thompson', 'Infrastructure Service Manager', 'Aisha Patel', 'GreenGrid NOC'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Daniel Brooks', 'Account Manager', 'Carlos Martinez', 'Crestline Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Rachel Kim', 'Media Technology Manager', 'Tom Wilson', 'Nimbus Production Engineering'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Anna Keller', 'Plant Technology Manager', 'Lukas Weber', 'Oakridge Plant Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Wei Tan', 'Hospitality Account Manager', 'James Lim', 'HarborView Regional IT'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Laura Bennett', 'Research IT Manager', 'Kevin Moore', 'Summit Security Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Nathan Cooper', 'Client Service Manager', 'Sophie Martin', 'MetroBuild Digital Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'Robert Evans', 'Education Account Manager', 'Maria Gonzalez', 'Pioneer University IT Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'George Wilson', 'Insurance Account Director', 'Amelia Brown', 'SilverOak IT Leadership'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Eric Johnson', 'Defense Account Manager', 'Rachel Adams', 'Redwood Security Operations'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Ravi Menon', 'India Account Manager', 'Neha Kapoor', 'Coastal Foods IT Operations');