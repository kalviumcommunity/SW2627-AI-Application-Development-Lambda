-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    primary_region VARCHAR(50),
    timezone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert clients
INSERT INTO clients (account_id, company_name, industry, company_size, primary_region, timezone) VALUES
('ACC-1001', 'Northstar Health Systems', 'Healthcare', 'Enterprise', 'US', 'America/New_York'),
('ACC-1002', 'VertexPay Financial', 'Financial Services', 'Enterprise', 'US', 'America/Chicago'),
('ACC-1003', 'BluePeak Retail Group', 'Retail', 'Large', 'US', 'America/Los_Angeles'),
('ACC-1004', 'Atlas Legal Partners', 'Legal Services', 'Mid-Market', 'UK', 'Europe/London'),
('ACC-1005', 'GreenGrid Energy', 'Energy & Utilities', 'Enterprise', 'Canada', 'America/Toronto'),
('ACC-1006', 'Crestline Logistics', 'Transportation & Logistics', 'Large', 'US', 'America/Denver'),
('ACC-1007', 'Nimbus Media Studios', 'Media & Entertainment', 'Mid-Market', 'US', 'America/Los_Angeles'),
('ACC-1008', 'Oakridge Manufacturing', 'Manufacturing', 'Large', 'Germany', 'Europe/Berlin'),
('ACC-1009', 'HarborView Hotels', 'Hospitality', 'Enterprise', 'Singapore', 'Asia/Singapore'),
('ACC-1010', 'Summit Biotech', 'Biotechnology', 'Mid-Market', 'US', 'America/New_York'),
('ACC-1011', 'MetroBuild Construction', 'Construction', 'Large', 'Australia', 'Australia/Sydney'),
('ACC-1012', 'Pioneer University', 'Education', 'Enterprise', 'US', 'America/New_York'),
('ACC-1013', 'SilverOak Insurance', 'Insurance', 'Enterprise', 'UK', 'Europe/London'),
('ACC-1014', 'Redwood Aerospace', 'Aerospace & Defense', 'Enterprise', 'US', 'America/Los_Angeles'),
('ACC-1015', 'Coastal Foods International', 'Food & Beverage', 'Large', 'India', 'Asia/Kolkata');