-- SLAs table
CREATE TABLE slas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    sla_id VARCHAR(50) UNIQUE NOT NULL,
    effective_date DATE NOT NULL,
    review_date DATE NOT NULL,
    support_model VARCHAR(50) NOT NULL,
    availability_target_percent DECIMAL(5,2),
    sla_clock VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert SLAs
INSERT INTO slas (client_id, sla_id, effective_date, review_date, support_model, availability_target_percent, sla_clock) VALUES
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'SLA-1001', '2026-01-01', '2026-12-31', '24x7', 99.95, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'SLA-1002', '2026-02-01', '2027-01-31', '24x7', 99.99, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'SLA-1003', '2026-01-15', '2027-01-14', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'SLA-1004', '2026-03-01', '2027-02-28', 'Business Hours + Emergency', 99.5, 'Business Hours'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'SLA-1005', '2026-01-01', '2026-12-31', '24x7', 99.99, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'SLA-1006', '2026-02-15', '2027-02-14', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'SLA-1007', '2026-01-01', '2026-12-31', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'SLA-1008', '2026-04-01', '2027-03-31', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'SLA-1009', '2026-01-01', '2026-12-31', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'SLA-1010', '2026-02-01', '2027-01-31', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'SLA-1011', '2026-01-01', '2026-12-31', 'Business Hours + Emergency', 99.5, 'Business Hours'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'SLA-1012', '2026-07-01', '2027-06-30', '24x7', 99.9, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'SLA-1013', '2026-01-01', '2026-12-31', '24x7', 99.95, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'SLA-1014', '2026-05-01', '2027-04-30', '24x7', 99.95, '24x7'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'SLA-1015', '2026-01-01', '2026-12-31', '24x7', 99.9, '24x7');
