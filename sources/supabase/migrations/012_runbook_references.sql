-- Runbook references table
CREATE TABLE runbook_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    runbook_reference VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert runbook references
INSERT INTO runbook_references (client_id, runbook_reference) VALUES
-- ACC-1001: Northstar Health Systems
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'RB-NSH-PROD-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'RB-NSH-EHR-INCIDENT'),
((SELECT id FROM clients WHERE account_id = 'ACC-1001'), 'RB-NSH-NETWORK-FAILURE'),
-- ACC-1002: VertexPay Financial
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'RB-VP-PAYMENT-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'RB-VP-DATABASE-FAILOVER'),
((SELECT id FROM clients WHERE account_id = 'ACC-1002'), 'RB-VP-FRAUD-SERVICE'),
-- ACC-1003: BluePeak Retail Group
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'RB-BPR-POS-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'RB-BPR-STORE-NETWORK'),
((SELECT id FROM clients WHERE account_id = 'ACC-1003'), 'RB-BPR-Ecommerce'),
-- ACC-1004: Atlas Legal Partners
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'RB-AL-M365-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'RB-AL-VPN'),
((SELECT id FROM clients WHERE account_id = 'ACC-1004'), 'RB-AL-DOCUMENT-MGMT'),
-- ACC-1005: GreenGrid Energy
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'RB-GGE-NETWORK-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'RB-GGE-SCADA'),
((SELECT id FROM clients WHERE account_id = 'ACC-1005'), 'RB-GGE-DATACENTER'),
-- ACC-1006: Crestline Logistics
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'RB-CL-WMS-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'RB-CL-WIFI'),
((SELECT id FROM clients WHERE account_id = 'ACC-1006'), 'RB-CL-FLEET-TRACKING'),
-- ACC-1007: Nimbus Media Studios
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'RB-NMS-STORAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'RB-NMS-RENDER-FARM'),
((SELECT id FROM clients WHERE account_id = 'ACC-1007'), 'RB-NMS-STUDIO-NETWORK'),
-- ACC-1008: Oakridge Manufacturing
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'RB-OM-PLANT-NETWORK'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'RB-OM-MES-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1008'), 'RB-OM-ERP'),
-- ACC-1009: HarborView Hotels
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'RB-HVH-PMS-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'RB-HVH-GUEST-WIFI'),
((SELECT id FROM clients WHERE account_id = 'ACC-1009'), 'RB-HVH-PAYMENT'),
-- ACC-1010: Summit Biotech
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'RB-SB-LAB-SYSTEM'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'RB-SB-CLOUD-STORAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1010'), 'RB-SB-SECURITY-INCIDENT'),
-- ACC-1011: MetroBuild Construction
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'RB-MBC-M365'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'RB-MBC-FIELD-NETWORK'),
((SELECT id FROM clients WHERE account_id = 'ACC-1011'), 'RB-MBC-PROJECT-PLATFORM'),
-- ACC-1012: Pioneer University
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'RB-PU-CAMPUS-NETWORK'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'RB-PU-LMS'),
((SELECT id FROM clients WHERE account_id = 'ACC-1012'), 'RB-PU-IDENTITY'),
-- ACC-1013: SilverOak Insurance
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'RB-SOI-CLAIMS-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'RB-SOI-DATABASE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1013'), 'RB-SOI-CUSTOMER-PORTAL'),
-- ACC-1014: Redwood Aerospace
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'RB-RA-SECURITY-INCIDENT'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'RB-RA-ENGINEERING'),
((SELECT id FROM clients WHERE account_id = 'ACC-1014'), 'RB-RA-IDENTITY'),
-- ACC-1015: Coastal Foods International
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'RB-CFI-ERP-OUTAGE'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'RB-CFI-WMS'),
((SELECT id FROM clients WHERE account_id = 'ACC-1015'), 'RB-CFI-PLANT-NETWORK');