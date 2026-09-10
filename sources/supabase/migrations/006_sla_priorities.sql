-- SLA priorities table
CREATE TABLE sla_priorities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sla_id UUID NOT NULL REFERENCES slas(id) ON DELETE CASCADE,
    priority_level VARCHAR(10) NOT NULL,
    priority_name VARCHAR(50) NOT NULL,
    definition TEXT,
    response_target_minutes INTEGER,
    restore_target_hours INTEGER,
    update_frequency_minutes INTEGER,
    update_frequency_hours INTEGER,
    response_target_business_hours INTEGER,
    resolution_target_business_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert SLA priorities for each SLA
INSERT INTO sla_priorities (sla_id, priority_level, priority_name, definition, response_target_minutes, restore_target_hours, update_frequency_minutes, update_frequency_hours, response_target_business_hours, resolution_target_business_days) VALUES
-- SLA-1001: Northstar Health Systems
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'P1', 'Critical', 'Complete outage or severe degradation of a critical clinical or infrastructure service affecting multiple facilities or patient care operations.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'P2', 'High', 'Major degradation affecting a department or critical workflow with limited workaround.', 30, 8, 60, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'P3', 'Medium', 'Localized issue affecting a limited number of users where a workaround exists.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1001'), 'P4', 'Low', 'Routine request, minor issue, informational request, or non-critical configuration change.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1002: VertexPay Financial
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'P1', 'Critical', 'Payment processing unavailable or widespread transaction failure.', 10, 2, 15, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'P2', 'High', 'Material degradation of payment or authentication services.', 20, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'P3', 'Medium', 'Limited application degradation with workaround.', 60, 12, NULL, 2, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1002'), 'P4', 'Low', 'General request or non-production issue.', NULL, NULL, NULL, NULL, 4, 3),
-- SLA-1003: BluePeak Retail Group
((SELECT id FROM slas WHERE sla_id = 'SLA-1003'), 'P1', 'Critical', 'Multiple stores unable to process sales or enterprise-wide e-commerce outage.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1003'), 'P2', 'High', 'One or more stores experiencing major POS or network disruption.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1003'), 'P3', 'Medium', 'Single-store or limited-user issue with workaround.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1003'), 'P4', 'Low', 'Standard service request or minor issue.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1004: Atlas Legal Partners
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'P1', 'Critical', 'Firm-wide outage or inability to access case-critical systems.', 30, 4, 60, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'P2', 'High', 'Multiple lawyers or a major practice group blocked from working.', 60, 8, NULL, 2, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'P3', 'Medium', 'Individual user issue with workaround.', NULL, NULL, NULL, NULL, 4, 2),
((SELECT id FROM slas WHERE sla_id = 'SLA-1004'), 'P4', 'Low', 'Routine request or minor issue.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1005: GreenGrid Energy
((SELECT id FROM slas WHERE sla_id = 'SLA-1005'), 'P1', 'Critical', 'Failure affecting operational monitoring or critical utility infrastructure.', 10, 2, 15, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1005'), 'P2', 'High', 'Major degradation affecting operational teams.', 20, 6, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1005'), 'P3', 'Medium', 'Non-critical infrastructure issue with workaround.', 60, 12, NULL, 2, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1005'), 'P4', 'Low', 'Routine infrastructure request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1006: Crestline Logistics
((SELECT id FROM slas WHERE sla_id = 'SLA-1006'), 'P1', 'Critical', 'Warehouse operations halted or fleet tracking unavailable across multiple sites.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1006'), 'P2', 'High', 'Major warehouse or logistics workflow degraded.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1006'), 'P3', 'Medium', 'Localized warehouse issue with workaround.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1006'), 'P4', 'Low', 'Routine request or minor issue.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1007: Nimbus Media Studios
((SELECT id FROM slas WHERE sla_id = 'SLA-1007'), 'P1', 'Critical', 'Production storage or studio infrastructure unavailable during active production.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1007'), 'P2', 'High', 'Major production workflow degraded.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1007'), 'P3', 'Medium', 'Individual production team issue with workaround.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1007'), 'P4', 'Low', 'Routine workstation or access request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1008: Oakridge Manufacturing
((SELECT id FROM slas WHERE sla_id = 'SLA-1008'), 'P1', 'Critical', 'Production line stopped due to supported IT infrastructure failure.', 15, 3, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1008'), 'P2', 'High', 'Production process materially degraded but operational workaround exists.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1008'), 'P3', 'Medium', 'Localized plant IT issue.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1008'), 'P4', 'Low', 'Routine request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1009: HarborView Hotels
((SELECT id FROM slas WHERE sla_id = 'SLA-1009'), 'P1', 'Critical', 'Hotel property unable to check in guests, process payments, or access core property systems.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1009'), 'P2', 'High', 'Major property system degradation affecting hotel operations.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1009'), 'P3', 'Medium', 'Localized guest or staff technology issue.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1009'), 'P4', 'Low', 'Routine request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1010: Summit Biotech
((SELECT id FROM slas WHERE sla_id = 'SLA-1010'), 'P1', 'Critical', 'Loss of access to research systems or confirmed security incident affecting regulated data.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1010'), 'P2', 'High', 'Major research workflow unavailable.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1010'), 'P3', 'Medium', 'Localized research technology issue.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1010'), 'P4', 'Low', 'Routine request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1011: MetroBuild Construction
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'P1', 'Critical', 'Enterprise-wide outage or project-critical system unavailable.', 30, 4, 60, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'P2', 'High', 'Major project team or site affected.', 60, 8, NULL, 2, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'P3', 'Medium', 'Individual site or user issue.', NULL, NULL, NULL, NULL, 4, 2),
((SELECT id FROM slas WHERE sla_id = 'SLA-1011'), 'P4', 'Low', 'Routine service request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1012: Pioneer University
((SELECT id FROM slas WHERE sla_id = 'SLA-1012'), 'P1', 'Critical', 'Campus-wide outage or student/academic system unavailable.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1012'), 'P2', 'High', 'Major campus service degraded.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1012'), 'P3', 'Medium', 'Localized issue affecting a department or group.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1012'), 'P4', 'Low', 'Routine service request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1013: SilverOak Insurance
((SELECT id FROM slas WHERE sla_id = 'SLA-1013'), 'P1', 'Critical', 'Claims or policy processing unavailable for a significant portion of users.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1013'), 'P2', 'High', 'Major business function impaired.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1013'), 'P3', 'Medium', 'Limited user impact with workaround.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1013'), 'P4', 'Low', 'Routine request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1014: Redwood Aerospace
((SELECT id FROM slas WHERE sla_id = 'SLA-1014'), 'P1', 'Critical', 'Critical engineering or manufacturing system unavailable, or suspected security compromise.', 10, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1014'), 'P2', 'High', 'Major operational degradation.', 30, 8, NULL, 1, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1014'), 'P3', 'Medium', 'Localized operational issue.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1014'), 'P4', 'Low', 'Routine service request.', NULL, NULL, NULL, NULL, 8, 5),
-- SLA-1015: Coastal Foods International
((SELECT id FROM slas WHERE sla_id = 'SLA-1015'), 'P1', 'Critical', 'Production or distribution operations halted due to supported IT failure.', 15, 4, 30, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1015'), 'P2', 'High', 'Major production or distribution workflow degraded.', 30, 8, 1, NULL, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1015'), 'P3', 'Medium', 'Localized business system issue with workaround.', 120, 24, NULL, 4, NULL, NULL),
((SELECT id FROM slas WHERE sla_id = 'SLA-1015'), 'P4', 'Low', 'Routine service request.', NULL, NULL, NULL, NULL, 8, 5);