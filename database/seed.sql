-- =============================================================================
-- Zigmaa Tech - Initial Seed Data Script
-- =============================================================================

-- Seed Roles (Matching ERD Workflow)
INSERT INTO roles (name, description, is_active) VALUES
('Super Admin', 'Full system access and approval rights', true),
('HR', 'Manage employees, leave requests, and administrative tasks', true),
('Team Leader', 'Assign work, monitor task progress, and lead project teams', true),
('Employee', 'Execute assigned tasks and log attendance', true)
ON CONFLICT (name) DO NOTHING;

-- Seed Departments
INSERT INTO departments (name, description, is_active) VALUES
('Engineering & IT', 'Software Development, System Architecture, and Infrastructure', true),
('Human Resources', 'Recruitment, People Management, and Internal Operations', true),
('Sales & Marketing', 'Client Acquisition, Marketing Campaigns, and Quotations', true),
('Finance & Accounts', 'Financial Management, Invoicing, and Accounting', true)
ON CONFLICT (name) DO NOTHING;
