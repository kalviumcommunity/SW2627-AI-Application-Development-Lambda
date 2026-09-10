-- SLA pause conditions table
CREATE TABLE sla_pause_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sla_id UUID NOT NULL REFERENCES slas(id) ON DELETE CASCADE,
    condition TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert SLA pause conditions
INSERT INTO sla_pause_conditions (sla_id, condition) VALUES
-- SLA-1001: Northstar Health Systems
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'Waiting for customer approval'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'Waiting for customer-provided access'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'Third-party vendor dependency'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'Customer-requested maintenance window'),
-- SLA-1002: VertexPay Financial
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'Customer approval pending'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'Third-party payment processor outage'),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'Scheduled maintenance');