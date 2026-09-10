-- Business hours table (for SLAs with business hours support)
CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sla_id UUID NOT NULL REFERENCES slas(id) ON DELETE CASCADE,
    day VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) NOT NULL
);

-- Insert business hours for SLAs that have them
INSERT INTO business_hours (sla_id, day, start_time, end_time, timezone) VALUES
-- SLA-1004: Atlas Legal Partners
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'Monday', '08:00', '18:00', 'Europe/London'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'Tuesday', '08:00', '18:00', 'Europe/London'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'Wednesday', '08:00', '18:00', 'Europe/London'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'Thursday', '08:00', '18:00', 'Europe/London'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'Friday', '08:00', '18:00', 'Europe/London'),
-- SLA-1011: MetroBuild Construction
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'Monday', '07:00', '18:00', 'Australia/Sydney'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'Tuesday', '07:00', '18:00', 'Australia/Sydney'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'Wednesday', '07:00', '18:00', 'Australia/Sydney'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'Thursday', '07:00', '18:00', 'Australia/Sydney'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'Friday', '07:00', '18:00', 'Australia/Sydney');
