-- SLA service credits table
CREATE TABLE sla_service_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sla_id UUID NOT NULL REFERENCES slas(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT FALSE,
    maximum_monthly_credit_percent DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert SLA service credits
INSERT INTO sla_service_credits (sla_id, enabled, maximum_monthly_credit_percent) VALUES
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), TRUE, 25.00),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), TRUE, 30.00);