-- SLA escalation table
CREATE TABLE sla_escalation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sla_id UUID NOT NULL REFERENCES slas(id) ON DELETE CASCADE,
    p1_after_minutes INTEGER,
    executive_notification_after_minutes INTEGER,
    incident_commander_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert SLA escalation rules
INSERT INTO sla_escalation (sla_id, p1_after_minutes, executive_notification_after_minutes, incident_commander_required) VALUES
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 15, 60, TRUE),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 10, 30, TRUE);