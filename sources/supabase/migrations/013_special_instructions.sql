-- Special instructions table
CREATE TABLE special_instructions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    instruction TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert special instructions
INSERT INTO special_instructions (client_id, instruction) VALUES
-- ACC-1001: Northstar Health Systems
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Security incidents involving patient data must be escalated immediately.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'Do not restart EHR production servers without customer IT approval.'),
-- ACC-1002: VertexPay Financial
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'Do not modify transaction databases without approval from the VertexPay DBA team.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'All suspected payment-data security incidents require immediate escalation.'),
-- ACC-1003: BluePeak Retail Group
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'During major retail events, P1 incidents must be escalated immediately.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'Store managers must not be instructed to factory-reset POS terminals.'),
-- ACC-1004: Atlas Legal Partners
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Do not access or modify client matter files unless explicitly authorized.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'Security incidents involving privileged legal documents require immediate escalation.'),
-- ACC-1005: GreenGrid Energy
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Never directly modify operational control systems without customer authorization.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'Operational technology incidents require NOC escalation.'),
-- ACC-1006: Crestline Logistics
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Warehouse outages affecting shipping cutoffs must be treated as P1.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'Coordinate with local warehouse management before restarting network equipment.'),
-- ACC-1007: Nimbus Media Studios
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Never delete media assets as part of incident remediation.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'Production incidents during live shoots receive P1 priority.'),
-- ACC-1008: Oakridge Manufacturing
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Do not reboot industrial controllers.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'Coordinate all plant network changes with the local OT engineer.'),
-- ACC-1009: HarborView Hotels
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Guest-facing outages take precedence over back-office issues.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'Payment terminal incidents must be coordinated with hotel finance.'),
-- ACC-1010: Summit Biotech
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Do not delete research data during troubleshooting.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'Suspected data exposure must immediately involve the security team.'),
-- ACC-1011: MetroBuild Construction
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'Site connectivity issues affecting active construction operations are escalated ahead of office requests.'),
-- ACC-1012: Pioneer University
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'During examination periods, LMS and identity incidents are automatically treated as P1.'),
-- ACC-1013: SilverOak Insurance
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Regulatory reporting deadlines require priority escalation.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'Security incidents must be coordinated with SilverOak Security Operations.'),
-- ACC-1014: Redwood Aerospace
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Do not transfer restricted data to non-approved systems.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'Security incidents must follow the customer security incident response process.'),
-- ACC-1015: Coastal Foods International
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Production-impacting ERP incidents are P1 regardless of number of affected users.'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'Plant changes require approval from the local IT lead.');