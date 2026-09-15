-- =============================================================================
-- Zigmaa Tech - IT Department CRM Database Schema
-- Database Engine: PostgreSQL 14+
-- Generated based on official ERD Diagram
-- =============================================================================

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS task_comments CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS project_members CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS quotations CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- -----------------------------------------------------------------------------
-- 1. ROLES
-- -----------------------------------------------------------------------------
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. USERS
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    manager_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_manager ON users(manager_id);
CREATE INDEX idx_users_email ON users(email);

-- -----------------------------------------------------------------------------
-- 3. DEPARTMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 4. EMPLOYEES
-- -----------------------------------------------------------------------------
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    department_id BIGINT NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    employee_code VARCHAR(50) NOT NULL UNIQUE,
    designation VARCHAR(100) NOT NULL,
    date_of_joining DATE NOT NULL,
    salary DECIMAL(12,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_user ON employees(user_id);

-- -----------------------------------------------------------------------------
-- 5. CLIENTS
-- -----------------------------------------------------------------------------
CREATE TABLE clients (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gst_number VARCHAR(50),
    address TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clients_created_by ON clients(created_by);
CREATE INDEX idx_clients_status ON clients(status);

-- -----------------------------------------------------------------------------
-- 6. QUOTATIONS
-- -----------------------------------------------------------------------------
CREATE TABLE quotations (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    quotation_no VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    gst DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    valid_till DATE NOT NULL,
    pdf_file VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotations_client ON quotations(client_id);
CREATE INDEX idx_quotations_created_by ON quotations(created_by);

-- -----------------------------------------------------------------------------
-- 7. PROJECTS
-- -----------------------------------------------------------------------------
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'planning',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_client ON projects(client_id);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_status ON projects(status);

-- -----------------------------------------------------------------------------
-- 8. PROJECT_MEMBERS
-- -----------------------------------------------------------------------------
CREATE TABLE project_members (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_project_employee UNIQUE (project_id, employee_id)
);

CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_employee ON project_members(employee_id);

-- -----------------------------------------------------------------------------
-- 9. TASKS
-- -----------------------------------------------------------------------------
CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    assigned_to BIGINT NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    assigned_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'todo',
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    completed_at DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_assigned_by ON tasks(assigned_by);
CREATE INDEX idx_tasks_status ON tasks(status);

-- -----------------------------------------------------------------------------
-- 10. TASK_COMMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE task_comments (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_comments_task ON task_comments(task_id);
CREATE INDEX idx_task_comments_user ON task_comments(user_id);

-- -----------------------------------------------------------------------------
-- 11. ATTENDANCE
-- -----------------------------------------------------------------------------
CREATE TABLE attendance (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in TIME NOT NULL,
    check_out TIME,
    status VARCHAR(20) NOT NULL DEFAULT 'present',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_employee_date UNIQUE (employee_id, date)
);

CREATE INDEX idx_attendance_employee ON attendance(employee_id);
CREATE INDEX idx_attendance_date ON attendance(date);

-- -----------------------------------------------------------------------------
-- 12. LEAVE_REQUESTS
-- -----------------------------------------------------------------------------
CREATE TABLE leave_requests (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    approved_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    leave_type VARCHAR(50) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_approved_by ON leave_requests(approved_by);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);

-- -----------------------------------------------------------------------------
-- 13. ACCOUNTS
-- -----------------------------------------------------------------------------
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    account_type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_created_by ON accounts(created_by);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- -----------------------------------------------------------------------------
-- 14. DOCUMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    related_type VARCHAR(50) NOT NULL,
    related_id BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    uploaded_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_related ON documents(related_type, related_id);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

-- -----------------------------------------------------------------------------
-- 15. NOTIFICATIONS
-- -----------------------------------------------------------------------------
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    related_type VARCHAR(50),
    related_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
