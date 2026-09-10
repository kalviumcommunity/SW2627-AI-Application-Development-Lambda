-- Support table
CREATE TABLE support (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    primary_channel VARCHAR(100),
    secondary_channel VARCHAR(100),
    emergency_channel VARCHAR(100),
    after_hours VARCHAR(50),
    on_site_support BOOLEAN DEFAULT FALSE,
    on_site_response_hours INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert support information
INSERT INTO support (client_id, primary_channel, secondary_channel, emergency_channel, after_hours, on_site_support, on_site_response_hours) VALUES
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Priority hotline', 'Service portal', NULL, '24x7', TRUE, 4),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Emergency hotline', 'Service portal', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Service portal', 'Store operations hotline', NULL, '24x7', TRUE, 6),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Service portal', 'Email', 'Emergency hotline', 'P1 only', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'NOC hotline', 'Service portal', NULL, '24x7', TRUE, 2),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Operations hotline', 'Service portal', NULL, '24x7', TRUE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Production hotline', 'Service portal', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Plant IT hotline', 'Service portal', NULL, '24x7', TRUE, 3),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Hotel operations hotline', 'Service portal', NULL, '24x7', TRUE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Research IT hotline', 'Service portal', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Service portal', 'Project support hotline', NULL, 'P1 only', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'University IT portal', 'IT hotline', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Service portal', 'Major incident hotline', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Secure service portal', 'Operations hotline', NULL, '24x7', FALSE, NULL),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Service desk hotline', 'Service portal', NULL, '24x7', TRUE, NULL);