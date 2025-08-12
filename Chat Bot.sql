-- Oracle Database Complete Schema Script
-- Drop existing objects if they exist to ensure clean execution
BEGIN
    FOR c IN (SELECT table_name FROM user_tables WHERE table_name IN (
        'DEPARTMENTS', 'EMPLOYEES', 'GATEPASS', 'SECURITY_GUARDS',
        'LOCATIONS', 'PROJECTS', 'ATTENDANCE', 'VISITORS', 
        'ASSETS', 'MAINTENANCE', 'TRAINING', 'PAYROLL',
        'INCIDENTS', 'ACCESS_CARDS'
    )) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || c.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
    
    FOR s IN (SELECT sequence_name FROM user_sequences WHERE sequence_name LIKE '%_SEQ') LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

-- Create Sequences
CREATE SEQUENCE departments_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE locations_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE employees_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE security_guards_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE projects_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE gatepass_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE attendance_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE visitors_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE assets_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE maintenance_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE training_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE payroll_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE incidents_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE access_cards_seq START WITH 1 INCREMENT BY 1;

-- 1. LOCATIONS (Independent table)
CREATE TABLE LOCATIONS (
    location_id NUMBER PRIMARY KEY,
    location_name VARCHAR2(100) NOT NULL,
    address VARCHAR2(200),
    city VARCHAR2(50),
    state VARCHAR2(50),
    postal_code VARCHAR2(10),
    country VARCHAR2(50) DEFAULT 'USA',
    created_date DATE DEFAULT SYSDATE
);

-- 2. DEPARTMENTS (Depends on LOCATIONS)
CREATE TABLE DEPARTMENTS (
    dept_id NUMBER PRIMARY KEY,
    dept_name VARCHAR2(100) NOT NULL,
    dept_code VARCHAR2(10) UNIQUE,
    location_id NUMBER,
    budget NUMBER(12,2),
    manager_id NUMBER,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_dept_location FOREIGN KEY (location_id) REFERENCES LOCATIONS(location_id)
);

-- 3. EMPLOYEES (Depends on DEPARTMENTS)
CREATE TABLE EMPLOYEES (
    emp_id NUMBER PRIMARY KEY,
    emp_code VARCHAR2(20) UNIQUE NOT NULL,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) UNIQUE,
    phone VARCHAR2(20),
    hire_date DATE DEFAULT SYSDATE,
    job_title VARCHAR2(100),
    salary NUMBER(10,2),
    dept_id NUMBER,
    manager_id NUMBER,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_emp_dept FOREIGN KEY (dept_id) REFERENCES DEPARTMENTS(dept_id),
    CONSTRAINT fk_emp_manager FOREIGN KEY (manager_id) REFERENCES EMPLOYEES(emp_id)
);

-- 4. SECURITY_GUARDS (Depends on EMPLOYEES)
CREATE TABLE SECURITY_GUARDS (
    guard_id NUMBER PRIMARY KEY,
    emp_id NUMBER NOT NULL,
    license_number VARCHAR2(50) UNIQUE,
    certification_level VARCHAR2(20),
    shift_preference VARCHAR2(20),
    weapon_permit VARCHAR2(1) DEFAULT 'N',
    training_expiry DATE,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_guard_emp FOREIGN KEY (emp_id) REFERENCES EMPLOYEES(emp_id)
);

-- 5. PROJECTS (Depends on DEPARTMENTS and EMPLOYEES)
CREATE TABLE PROJECTS (
    project_id NUMBER PRIMARY KEY,
    project_name VARCHAR2(100) NOT NULL,
    project_code VARCHAR2(20) UNIQUE,
    description CLOB,
    start_date DATE,
    end_date DATE,
    budget NUMBER(12,2),
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    dept_id NUMBER,
    project_manager_id NUMBER,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_proj_dept FOREIGN KEY (dept_id) REFERENCES DEPARTMENTS(dept_id),
    CONSTRAINT fk_proj_manager FOREIGN KEY (project_manager_id) REFERENCES EMPLOYEES(emp_id)
);

-- 6. GATEPASS (Depends on EMPLOYEES and SECURITY_GUARDS)
CREATE TABLE GATEPASS (
    gatepass_id NUMBER PRIMARY KEY,
    gatepass_number VARCHAR2(50) UNIQUE NOT NULL,
    emp_id NUMBER NOT NULL,
    purpose VARCHAR2(200),
    exit_time TIMESTAMP,
    expected_return TIMESTAMP,
    actual_return TIMESTAMP,
    approved_by NUMBER,
    guard_out NUMBER,
    guard_in NUMBER,
    status VARCHAR2(20) DEFAULT 'PENDING',
    items_carried CLOB,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_gatepass_emp FOREIGN KEY (emp_id) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT fk_gatepass_approver FOREIGN KEY (approved_by) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT fk_gatepass_guard_out FOREIGN KEY (guard_out) REFERENCES SECURITY_GUARDS(guard_id),
    CONSTRAINT fk_gatepass_guard_in FOREIGN KEY (guard_in) REFERENCES SECURITY_GUARDS(guard_id)
);

-- 7. ATTENDANCE (Depends on EMPLOYEES)
CREATE TABLE ATTENDANCE (
    attendance_id NUMBER PRIMARY KEY,
    emp_id NUMBER NOT NULL,
    attendance_date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    total_hours NUMBER(4,2),
    overtime_hours NUMBER(4,2) DEFAULT 0,
    status VARCHAR2(20) DEFAULT 'PRESENT',
    remarks VARCHAR2(200),
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_att_emp FOREIGN KEY (emp_id) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT uk_emp_date UNIQUE (emp_id, attendance_date)
);

-- 8. VISITORS (Depends on EMPLOYEES and SECURITY_GUARDS)
CREATE TABLE VISITORS (
    visitor_id NUMBER PRIMARY KEY,
    visitor_name VARCHAR2(100) NOT NULL,
    company VARCHAR2(100),
    phone VARCHAR2(20),
    email VARCHAR2(100),
    purpose VARCHAR2(200),
    host_emp_id NUMBER,
    entry_time TIMESTAMP DEFAULT SYSTIMESTAMP,
    exit_time TIMESTAMP,
    id_type VARCHAR2(50),
    id_number VARCHAR2(50),
    guard_id NUMBER,
    status VARCHAR2(20) DEFAULT 'IN',
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_visitor_host FOREIGN KEY (host_emp_id) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT fk_visitor_guard FOREIGN KEY (guard_id) REFERENCES SECURITY_GUARDS(guard_id)
);

-- 9. ASSETS (Depends on EMPLOYEES and DEPARTMENTS)
CREATE TABLE ASSETS (
    asset_id NUMBER PRIMARY KEY,
    asset_tag VARCHAR2(50) UNIQUE NOT NULL,
    asset_name VARCHAR2(100) NOT NULL,
    category VARCHAR2(50),
    brand VARCHAR2(50),
    model VARCHAR2(50),
    serial_number VARCHAR2(100),
    purchase_date DATE,
    purchase_cost NUMBER(12,2),
    assigned_to NUMBER,
    dept_id NUMBER,
    location_id NUMBER,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    warranty_expiry DATE,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_asset_emp FOREIGN KEY (assigned_to) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT fk_asset_dept FOREIGN KEY (dept_id) REFERENCES DEPARTMENTS(dept_id),
    CONSTRAINT fk_asset_location FOREIGN KEY (location_id) REFERENCES LOCATIONS(location_id)
);

-- 10. MAINTENANCE (Depends on ASSETS and EMPLOYEES)
CREATE TABLE MAINTENANCE (
    maintenance_id NUMBER PRIMARY KEY,
    asset_id NUMBER NOT NULL,
    maintenance_type VARCHAR2(50),
    description CLOB,
    scheduled_date DATE,
    completed_date DATE,
    technician_id NUMBER,
    cost NUMBER(10,2),
    status VARCHAR2(20) DEFAULT 'SCHEDULED',
    next_maintenance DATE,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_maint_asset FOREIGN KEY (asset_id) REFERENCES ASSETS(asset_id),
    CONSTRAINT fk_maint_tech FOREIGN KEY (technician_id) REFERENCES EMPLOYEES(emp_id)
);

-- 11. TRAINING (Depends on EMPLOYEES)
CREATE TABLE TRAINING (
    training_id NUMBER PRIMARY KEY,
    training_name VARCHAR2(100) NOT NULL,
    description CLOB,
    trainer_name VARCHAR2(100),
    start_date DATE,
    end_date DATE,
    max_participants NUMBER,
    cost_per_participant NUMBER(8,2),
    location_id NUMBER,
    status VARCHAR2(20) DEFAULT 'SCHEDULED',
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_training_location FOREIGN KEY (location_id) REFERENCES LOCATIONS(location_id)
);

-- 12. PAYROLL (Depends on EMPLOYEES)
CREATE TABLE PAYROLL (
    payroll_id NUMBER PRIMARY KEY,
    emp_id NUMBER NOT NULL,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    basic_salary NUMBER(10,2),
    overtime_pay NUMBER(8,2) DEFAULT 0,
    allowances NUMBER(8,2) DEFAULT 0,
    deductions NUMBER(8,2) DEFAULT 0,
    gross_pay NUMBER(10,2),
    tax_deducted NUMBER(8,2),
    net_pay NUMBER(10,2),
    pay_date DATE,
    status VARCHAR2(20) DEFAULT 'CALCULATED',
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_payroll_emp FOREIGN KEY (emp_id) REFERENCES EMPLOYEES(emp_id)
);

-- 13. INCIDENTS (Depends on EMPLOYEES and SECURITY_GUARDS)
CREATE TABLE INCIDENTS (
    incident_id NUMBER PRIMARY KEY,
    incident_number VARCHAR2(50) UNIQUE NOT NULL,
    incident_type VARCHAR2(50),
    description CLOB,
    incident_date TIMESTAMP DEFAULT SYSTIMESTAMP,
    location_id NUMBER,
    reported_by NUMBER,
    assigned_guard NUMBER,
    severity_level VARCHAR2(20),
    status VARCHAR2(20) DEFAULT 'OPEN',
    resolution CLOB,
    resolved_date DATE,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_incident_location FOREIGN KEY (location_id) REFERENCES LOCATIONS(location_id),
    CONSTRAINT fk_incident_reporter FOREIGN KEY (reported_by) REFERENCES EMPLOYEES(emp_id),
    CONSTRAINT fk_incident_guard FOREIGN KEY (assigned_guard) REFERENCES SECURITY_GUARDS(guard_id)
);

-- 14. ACCESS_CARDS (Depends on EMPLOYEES)
CREATE TABLE ACCESS_CARDS (
    card_id NUMBER PRIMARY KEY,
    card_number VARCHAR2(50) UNIQUE NOT NULL,
    emp_id NUMBER NOT NULL,
    card_type VARCHAR2(50),
    issued_date DATE DEFAULT SYSDATE,
    expiry_date DATE,
    access_level VARCHAR2(50),
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    last_used TIMESTAMP,
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT fk_card_emp FOREIGN KEY (emp_id) REFERENCES EMPLOYEES(emp_id)
);

-- Now add the manager_id foreign key to departments after employees table is created
ALTER TABLE DEPARTMENTS ADD CONSTRAINT fk_dept_manager 
FOREIGN KEY (manager_id) REFERENCES EMPLOYEES(emp_id);

-- Insert sample data in proper order to avoid foreign key violations

-- Insert LOCATIONS (10 rows)
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Headquarters', '123 Business St', 'New York', 'NY', '10001', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'West Coast Office', '456 Tech Ave', 'San Francisco', 'CA', '94102', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'East Coast Branch', '789 Finance Blvd', 'Boston', 'MA', '02101', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'South Office', '321 Corporate Dr', 'Atlanta', 'GA', '30301', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Midwest Center', '654 Industrial Rd', 'Chicago', 'IL', '60601', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Southwest Hub', '987 Innovation Way', 'Austin', 'TX', '73301', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Northwest Branch', '147 Mountain View', 'Seattle', 'WA', '98101', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Central Office', '258 Plains Ave', 'Denver', 'CO', '80201', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Remote Center', '369 Digital St', 'Phoenix', 'AZ', '85001', 'USA', SYSDATE);
INSERT INTO LOCATIONS VALUES (locations_seq.NEXTVAL, 'Satellite Office', '741 Connect Blvd', 'Miami', 'FL', '33101', 'USA', SYSDATE);

-- Insert DEPARTMENTS (10 rows)
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Information Technology', 'IT', 1, 500000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Human Resources', 'HR', 1, 200000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Finance', 'FIN', 3, 300000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Operations', 'OPS', 4, 400000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Marketing', 'MKT', 2, 250000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Security', 'SEC', 1, 150000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Legal', 'LEG', 3, 180000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Procurement', 'PROC', 5, 120000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Research & Development', 'RND', 2, 600000, NULL, SYSDATE);
INSERT INTO DEPARTMENTS VALUES (departments_seq.NEXTVAL, 'Quality Assurance', 'QA', 6, 220000, NULL, SYSDATE);

-- Insert EMPLOYEES (10 rows)
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP001', 'John', 'Smith', 'john.smith@company.com', '555-0101', DATE '2020-01-15', 'IT Manager', 85000, 1, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP002', 'Sarah', 'Johnson', 'sarah.johnson@company.com', '555-0102', DATE '2019-03-20', 'HR Director', 75000, 2, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP003', 'Mike', 'Davis', 'mike.davis@company.com', '555-0103', DATE '2021-06-10', 'Financial Analyst', 65000, 3, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP004', 'Lisa', 'Wilson', 'lisa.wilson@company.com', '555-0104', DATE '2020-09-05', 'Operations Manager', 70000, 4, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP005', 'David', 'Brown', 'david.brown@company.com', '555-0105', DATE '2022-01-12', 'Marketing Specialist', 55000, 5, 2, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP006', 'Jennifer', 'Garcia', 'jennifer.garcia@company.com', '555-0106', DATE '2018-11-30', 'Security Chief', 68000, 6, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP007', 'Robert', 'Martinez', 'robert.martinez@company.com', '555-0107', DATE '2019-08-22', 'Legal Counsel', 90000, 7, NULL, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP008', 'Amanda', 'Taylor', 'amanda.taylor@company.com', '555-0108', DATE '2021-04-15', 'Procurement Officer', 58000, 8, 4, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP009', 'Christopher', 'Anderson', 'chris.anderson@company.com', '555-0109', DATE '2020-07-08', 'R&D Engineer', 72000, 9, 1, 'ACTIVE', SYSDATE);
INSERT INTO EMPLOYEES VALUES (employees_seq.NEXTVAL, 'EMP010', 'Michelle', 'Thomas', 'michelle.thomas@company.com', '555-0110', DATE '2019-12-03', 'QA Manager', 66000, 10, NULL, 'ACTIVE', SYSDATE);

-- Update department managers
UPDATE DEPARTMENTS SET manager_id = 1 WHERE dept_id = 1;
UPDATE DEPARTMENTS SET manager_id = 2 WHERE dept_id = 2;
UPDATE DEPARTMENTS SET manager_id = 3 WHERE dept_id = 3;
UPDATE DEPARTMENTS SET manager_id = 4 WHERE dept_id = 4;
UPDATE DEPARTMENTS SET manager_id = 2 WHERE dept_id = 5;
UPDATE DEPARTMENTS SET manager_id = 6 WHERE dept_id = 6;
UPDATE DEPARTMENTS SET manager_id = 7 WHERE dept_id = 7;
UPDATE DEPARTMENTS SET manager_id = 8 WHERE dept_id = 8;
UPDATE DEPARTMENTS SET manager_id = 9 WHERE dept_id = 9;
UPDATE DEPARTMENTS SET manager_id = 10 WHERE dept_id = 10;

-- Insert SECURITY_GUARDS (10 rows)
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 6, 'SEC001', 'Level 3', 'Day', 'Y', DATE '2025-12-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 1, 'SEC002', 'Level 2', 'Night', 'N', DATE '2024-06-30', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 4, 'SEC003', 'Level 1', 'Day', 'N', DATE '2024-12-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 2, 'SEC004', 'Level 2', 'Evening', 'Y', DATE '2025-03-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 8, 'SEC005', 'Level 1', 'Night', 'N', DATE '2024-09-30', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 3, 'SEC006', 'Level 3', 'Day', 'Y', DATE '2025-08-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 7, 'SEC007', 'Level 2', 'Evening', 'N', DATE '2024-11-30', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 10, 'SEC008', 'Level 1', 'Day', 'N', DATE '2025-01-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 5, 'SEC009', 'Level 2', 'Night', 'Y', DATE '2025-05-31', 'ACTIVE', SYSDATE);
INSERT INTO SECURITY_GUARDS VALUES (security_guards_seq.NEXTVAL, 9, 'SEC010', 'Level 3', 'Evening', 'Y', DATE '2025-10-31', 'ACTIVE', SYSDATE);

-- Insert PROJECTS (10 rows)
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'ERP Implementation', 'PROJ001', 'Company-wide ERP system implementation', DATE '2024-01-01', DATE '2024-12-31', 200000, 'ACTIVE', 1, 1, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Office Renovation', 'PROJ002', 'Headquarters office space renovation', DATE '2024-03-01', DATE '2024-08-31', 150000, 'ACTIVE', 4, 4, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Marketing Campaign', 'PROJ003', 'New product launch campaign', DATE '2024-02-15', DATE '2024-07-15', 75000, 'ACTIVE', 5, 2, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Security Upgrade', 'PROJ004', 'Enhanced security systems installation', DATE '2024-04-01', DATE '2024-09-30', 100000, 'ACTIVE', 6, 6, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Financial Audit', 'PROJ005', 'Annual comprehensive financial audit', DATE '2024-01-15', DATE '2024-04-15', 50000, 'COMPLETED', 3, 3, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Training Program', 'PROJ006', 'Employee skill development program', DATE '2024-05-01', DATE '2024-10-31', 80000, 'ACTIVE', 2, 2, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Process Automation', 'PROJ007', 'Business process automation initiative', DATE '2024-06-01', DATE '2024-11-30', 120000, 'ACTIVE', 9, 9, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Quality Improvement', 'PROJ008', 'Quality management system enhancement', DATE '2024-03-15', DATE '2024-09-15', 90000, 'ACTIVE', 10, 10, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Legal Compliance', 'PROJ009', 'Regulatory compliance review', DATE '2024-02-01', DATE '2024-06-30', 60000, 'ACTIVE', 7, 7, SYSDATE);
INSERT INTO PROJECTS VALUES (projects_seq.NEXTVAL, 'Vendor Management', 'PROJ010', 'Supplier relationship optimization', DATE '2024-07-01', DATE '2024-12-31', 70000, 'ACTIVE', 8, 8, SYSDATE);

-- Insert GATEPASS (10 rows)
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP001', 1, 'Client Meeting', TIMESTAMP '2024-08-12 09:00:00', TIMESTAMP '2024-08-12 17:00:00', TIMESTAMP '2024-08-12 16:30:00', 6, 1, 2, 'COMPLETED', 'Laptop, Documents', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP002', 3, 'Bank Visit', TIMESTAMP '2024-08-12 14:00:00', TIMESTAMP '2024-08-12 16:00:00', NULL, 4, 3, NULL, 'ACTIVE', 'Financial Records', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP003', 5, 'Marketing Event', TIMESTAMP '2024-08-11 08:00:00', TIMESTAMP '2024-08-11 20:00:00', TIMESTAMP '2024-08-11 19:45:00', 2, 4, 5, 'COMPLETED', 'Promotional Materials', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP004', 7, 'Court Hearing', TIMESTAMP '2024-08-10 10:00:00', TIMESTAMP '2024-08-10 15:00:00', TIMESTAMP '2024-08-10 14:30:00', 6, 6, 7, 'COMPLETED', 'Legal Files', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP005', 2, 'Training Session', TIMESTAMP '2024-08-12 13:00:00', TIMESTAMP '2024-08-12 18:00:00', NULL, 6, 8, NULL, 'ACTIVE', 'Training Materials', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP006', 9, 'Research Conference', TIMESTAMP '2024-08-09 07:00:00', TIMESTAMP '2024-08-09 22:00:00', TIMESTAMP '2024-08-09 21:30:00', 1, 9, 10, 'COMPLETED', 'Research Equipment', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP007', 8, 'Supplier Meeting', TIMESTAMP '2024-08-12 11:00:00', TIMESTAMP '2024-08-12 14:00:00', NULL, 4, 1, NULL, 'ACTIVE', 'Contracts', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP008', 10, 'Quality Audit', TIMESTAMP '2024-08-11 12:00:00', TIMESTAMP '2024-08-11 17:00:00', TIMESTAMP '2024-08-11 16:45:00', 6, 2, 3, 'COMPLETED', 'Audit Checklist', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP009', 4, 'Operations Review', TIMESTAMP '2024-08-12 15:00:00', TIMESTAMP '2024-08-12 19:00:00', NULL, 6, 4, NULL, 'ACTIVE', 'Reports', SYSDATE);
INSERT INTO GATEPASS VALUES (gatepass_seq.NEXTVAL, 'GP010', 6, 'Security Training', TIMESTAMP '2024-08-08 08:00:00', TIMESTAMP '2024-08-08 17:00:00', TIMESTAMP '2024-08-08 16:50:00', 6, 5, 6, 'COMPLETED', 'Training Certificate', SYSDATE);

-- Insert ATTENDANCE (10 rows)
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 1, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:30:00', TIMESTAMP '2024-08-12 17:30:00', 9.00, 1.00, 'PRESENT', 'Regular day', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 2, DATE '2024-08-12', TIMESTAMP '2024-08-12 09:00:00', TIMESTAMP '2024-08-12 18:00:00', 9.00, 0.00, 'PRESENT', 'HR meeting', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 3, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:45:00', TIMESTAMP '2024-08-12 17:15:00', 8.50, 0.00, 'PRESENT', 'Left early', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 4, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:00:00', TIMESTAMP '2024-08-12 19:00:00', 11.00, 3.00, 'PRESENT', 'Overtime work', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 5, DATE '2024-08-12', TIMESTAMP '2024-08-12 09:15:00', TIMESTAMP '2024-08-12 17:45:00', 8.50, 0.00, 'PRESENT', 'Marketing event', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 6, DATE '2024-08-12', TIMESTAMP '2024-08-12 07:30:00', TIMESTAMP '2024-08-12 16:30:00', 9.00, 0.00, 'PRESENT', 'Security duties', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 7, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:30:00', TIMESTAMP '2024-08-12 17:30:00', 9.00, 0.00, 'PRESENT', 'Legal work', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 8, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:15:00', TIMESTAMP '2024-08-12 17:00:00', 8.75, 0.00, 'PRESENT', 'Procurement tasks', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 9, DATE '2024-08-12', TIMESTAMP '2024-08-12 08:45:00', TIMESTAMP '2024-08-12 18:30:00', 9.75, 1.75, 'PRESENT', 'R&D project', SYSDATE);
INSERT INTO ATTENDANCE VALUES (attendance_seq.NEXTVAL, 10, DATE '2024-08-12', TIMESTAMP '2024-08-12 09:00:00', TIMESTAMP '2024-08-12 17:30:00', 8.50, 0.00, 'PRESENT', 'QA reviews', SYSDATE);

-- Insert VISITORS (10 rows)
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Alice Cooper', 'TechCorp Inc', '555-2001', 'alice.cooper@techcorp.com', 'Business Meeting', 1, TIMESTAMP '2024-08-12 10:00:00', TIMESTAMP '2024-08-12 12:00:00', 'Driver License', 'DL123456789', 1, 'OUT', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Bob Wilson', 'Finance Solutions', '555-2002', 'bob.wilson@finsol.com', 'Financial Consultation', 3, TIMESTAMP '2024-08-12 14:30:00', NULL, 'Passport', 'PP987654321', 2, 'IN', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Carol Smith', 'Marketing Plus', '555-2003', 'carol.smith@mktplus.com', 'Marketing Discussion', 5, TIMESTAMP '2024-08-12 09:15:00', TIMESTAMP '2024-08-12 11:30:00', 'State ID', 'ID456789123', 3, 'OUT', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Daniel Brown', 'Operations Expert', '555-2004', 'daniel.brown@opexpert.com', 'Operations Review', 4, TIMESTAMP '2024-08-12 13:00:00', NULL, 'Driver License', 'DL789123456', 4, 'IN', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Emma Davis', 'HR Consulting', '555-2005', 'emma.davis@hrconsult.com', 'HR Strategy', 2, TIMESTAMP '2024-08-12 11:00:00', TIMESTAMP '2024-08-12 15:00:00', 'Passport', 'PP123789456', 5, 'OUT', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Frank Miller', 'Security Systems', '555-2006', 'frank.miller@secsys.com', 'Security Upgrade', 6, TIMESTAMP '2024-08-12 08:30:00', NULL, 'Driver License', 'DL654321987', 6, 'IN', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Grace Lee', 'Legal Associates', '555-2007', 'grace.lee@legalassoc.com', 'Legal Review', 7, TIMESTAMP '2024-08-12 15:30:00', NULL, 'State ID', 'ID987654321', 7, 'IN', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Henry Johnson', 'Procurement Services', '555-2008', 'henry.johnson@procserv.com', 'Vendor Meeting', 8, TIMESTAMP '2024-08-12 10:45:00', TIMESTAMP '2024-08-12 13:15:00', 'Driver License', 'DL321654987', 8, 'OUT', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Iris Chen', 'Research Institute', '555-2009', 'iris.chen@research.org', 'R&D Collaboration', 9, TIMESTAMP '2024-08-12 12:00:00', NULL, 'Passport', 'PP456123789', 9, 'IN', SYSDATE);
INSERT INTO VISITORS VALUES (visitors_seq.NEXTVAL, 'Jack Taylor', 'QA Solutions', '555-2010', 'jack.taylor@qasol.com', 'Quality Assessment', 10, TIMESTAMP '2024-08-12 14:00:00', TIMESTAMP '2024-08-12 16:30:00', 'State ID', 'ID147258369', 10, 'OUT', SYSDATE);

-- Insert ASSETS (10 rows)
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'LAP001', 'Dell Laptop', 'Computer', 'Dell', 'Latitude 5520', 'DL123456', DATE '2023-01-15', 1200.00, 1, 1, 1, 'ACTIVE', DATE '2026-01-15', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'DES001', 'HP Desktop', 'Computer', 'HP', 'EliteDesk 800', 'HP789123', DATE '2022-06-10', 800.00, 3, 3, 3, 'ACTIVE', DATE '2025-06-10', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'PRT001', 'Canon Printer', 'Printer', 'Canon', 'ImageCLASS MF445dw', 'CN456789', DATE '2023-03-20', 350.00, NULL, 2, 1, 'ACTIVE', DATE '2026-03-20', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'MON001', 'Samsung Monitor', 'Monitor', 'Samsung', '27" Curved', 'SM987654', DATE '2023-08-05', 300.00, 9, 9, 2, 'ACTIVE', DATE '2026-08-05', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'CAM001', 'Security Camera', 'Security', 'Hikvision', 'DS-2CD2143G0-I', 'HV123789', DATE '2022-12-01', 250.00, NULL, 6, 1, 'ACTIVE', DATE '2025-12-01', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'TAB001', 'iPad Tablet', 'Tablet', 'Apple', 'iPad Air', 'AP654321', DATE '2023-05-15', 600.00, 5, 5, 2, 'ACTIVE', DATE '2026-05-15', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'PHN001', 'Office Phone', 'Communication', 'Cisco', 'IP Phone 7841', 'CS789456', DATE '2022-09-20', 150.00, 7, 7, 3, 'ACTIVE', DATE '2025-09-20', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'PRJ001', 'Projector', 'Presentation', 'Epson', 'PowerLite 1795F', 'EP321654', DATE '2023-02-10', 450.00, NULL, 2, 1, 'ACTIVE', DATE '2026-02-10', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'SRV001', 'Dell Server', 'Server', 'Dell', 'PowerEdge R740', 'DL987123', DATE '2022-04-25', 3500.00, NULL, 1, 1, 'ACTIVE', DATE '2025-04-25', SYSDATE);
INSERT INTO ASSETS VALUES (assets_seq.NEXTVAL, 'UPS001', 'APC UPS', 'Power', 'APC', 'Smart-UPS 1500VA', 'AP456987', DATE '2023-07-30', 400.00, NULL, 1, 1, 'ACTIVE', DATE '2026-07-30', SYSDATE);

-- Insert MAINTENANCE (10 rows)
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 1, 'Preventive', 'Regular laptop maintenance and cleaning', DATE '2024-08-15', NULL, 1, 50.00, 'SCHEDULED', DATE '2024-11-15', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 2, 'Repair', 'Hard drive replacement', DATE '2024-08-10', DATE '2024-08-10', 9, 200.00, 'COMPLETED', DATE '2024-11-10', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 3, 'Preventive', 'Printer toner replacement and cleaning', DATE '2024-08-12', DATE '2024-08-12', 1, 75.00, 'COMPLETED', DATE '2024-11-12', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 5, 'Preventive', 'Security camera lens cleaning', DATE '2024-08-20', NULL, 6, 30.00, 'SCHEDULED', DATE '2024-11-20', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 9, 'Repair', 'Server cooling system repair', DATE '2024-08-05', DATE '2024-08-08', 1, 500.00, 'COMPLETED', DATE '2025-02-05', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 4, 'Preventive', 'Monitor calibration', DATE '2024-08-25', NULL, 9, 25.00, 'SCHEDULED', DATE '2024-11-25', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 6, 'Repair', 'iPad screen replacement', DATE '2024-07-30', DATE '2024-08-01', 1, 150.00, 'COMPLETED', DATE '2024-10-30', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 7, 'Preventive', 'Phone system update', DATE '2024-08-18', NULL, 1, 40.00, 'SCHEDULED', DATE '2024-11-18', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 8, 'Preventive', 'Projector filter cleaning', DATE '2024-08-22', NULL, 1, 35.00, 'SCHEDULED', DATE '2024-11-22', SYSDATE);
INSERT INTO MAINTENANCE VALUES (maintenance_seq.NEXTVAL, 10, 'Repair', 'UPS battery replacement', DATE '2024-08-14', DATE '2024-08-14', 1, 120.00, 'COMPLETED', DATE '2025-02-14', SYSDATE);

-- Insert TRAINING (10 rows)
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Cybersecurity Awareness', 'Basic cybersecurity training for all employees', 'John Security Expert', DATE '2024-08-15', DATE '2024-08-16', 50, 100.00, 1, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Leadership Development', 'Management and leadership skills training', 'Sarah Leadership Coach', DATE '2024-08-20', DATE '2024-08-22', 20, 250.00, 2, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Financial Planning', 'Budget management and financial planning', 'Mike Finance Guru', DATE '2024-08-25', DATE '2024-08-26', 30, 150.00, 3, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Project Management', 'PMP certification preparation course', 'Lisa PM Expert', DATE '2024-09-01', DATE '2024-09-05', 25, 300.00, 1, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Digital Marketing', 'Modern digital marketing strategies', 'David Marketing Pro', DATE '2024-08-18', DATE '2024-08-19', 40, 200.00, 2, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Emergency Response', 'Emergency procedures and first aid', 'Jennifer Safety Officer', DATE '2024-08-12', DATE '2024-08-12', 100, 75.00, 1, 'COMPLETED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Legal Compliance', 'Corporate compliance and regulations', 'Robert Legal Expert', DATE '2024-08-30', DATE '2024-08-31', 35, 180.00, 3, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Supply Chain Management', 'Modern supply chain optimization', 'Amanda Supply Expert', DATE '2024-09-10', DATE '2024-09-12', 20, 220.00, 5, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Innovation Workshop', 'Creative thinking and innovation', 'Chris Innovation Leader', DATE '2024-08-28', DATE '2024-08-29', 30, 175.00, 2, 'SCHEDULED', SYSDATE);
INSERT INTO TRAINING VALUES (training_seq.NEXTVAL, 'Quality Management', 'Six Sigma and quality improvement', 'Michelle Quality Expert', DATE '2024-09-15', DATE '2024-09-17', 25, 275.00, 6, 'SCHEDULED', SYSDATE);

-- Insert PAYROLL (10 rows)
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 1, DATE '2024-08-01', DATE '2024-08-31', 85000.00, 850.00, 1000.00, 500.00, 86350.00, 17270.00, 69080.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 2, DATE '2024-08-01', DATE '2024-08-31', 75000.00, 0.00, 800.00, 300.00, 75500.00, 15100.00, 60400.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 3, DATE '2024-08-01', DATE '2024-08-31', 65000.00, 325.00, 600.00, 200.00, 65725.00, 13145.00, 52580.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 4, DATE '2024-08-01', DATE '2024-08-31', 70000.00, 2100.00, 700.00, 250.00, 72550.00, 14510.00, 58040.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 5, DATE '2024-08-01', DATE '2024-08-31', 55000.00, 0.00, 500.00, 150.00, 55350.00, 11070.00, 44280.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 6, DATE '2024-08-01', DATE '2024-08-31', 68000.00, 0.00, 800.00, 400.00, 68400.00, 13680.00, 54720.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 7, DATE '2024-08-01', DATE '2024-08-31', 90000.00, 0.00, 1200.00, 600.00, 90600.00, 18120.00, 72480.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 8, DATE '2024-08-01', DATE '2024-08-31', 58000.00, 0.00, 600.00, 200.00, 58400.00, 11680.00, 46720.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 9, DATE '2024-08-01', DATE '2024-08-31', 72000.00, 1260.00, 900.00, 350.00, 73810.00, 14762.00, 59048.00, DATE '2024-09-05', 'PAID', SYSDATE);
INSERT INTO PAYROLL VALUES (payroll_seq.NEXTVAL, 10, DATE '2024-08-01', DATE '2024-08-31', 66000.00, 0.00, 700.00, 300.00, 66400.00, 13280.00, 53120.00, DATE '2024-09-05', 'PAID', SYSDATE);

-- Insert INCIDENTS (10 rows)
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC001', 'Security Breach', 'Unauthorized access attempt detected at main entrance', TIMESTAMP '2024-08-10 14:30:00', 1, 3, 1, 'HIGH', 'RESOLVED', 'Access logs reviewed, security protocols updated', DATE '2024-08-11', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC002', 'Fire Alarm', 'False fire alarm triggered in building B', TIMESTAMP '2024-08-08 10:15:00', 2, 4, 2, 'MEDIUM', 'RESOLVED', 'Smoke detector malfunction fixed', DATE '2024-08-08', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC003', 'Theft', 'Office supplies reported missing from storage', TIMESTAMP '2024-08-07 16:45:00', 1, 8, 3, 'MEDIUM', 'UNDER_INVESTIGATION', NULL, NULL, SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC004', 'Vandalism', 'Graffiti found on exterior wall', TIMESTAMP '2024-08-09 07:30:00', 1, 6, 4, 'LOW', 'RESOLVED', 'Wall cleaned, security footage reviewed', DATE '2024-08-09', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC005', 'Medical Emergency', 'Employee slip and fall in cafeteria', TIMESTAMP '2024-08-12 12:00:00', 1, 2, 5, 'HIGH', 'RESOLVED', 'First aid provided, incident reported to HR', DATE '2024-08-12', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC006', 'Power Outage', 'Partial power loss in east wing', TIMESTAMP '2024-08-11 15:20:00', 3, 1, 6, 'MEDIUM', 'RESOLVED', 'Electrical issue fixed by maintenance', DATE '2024-08-11', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC007', 'Suspicious Activity', 'Unknown individual loitering in parking lot', TIMESTAMP '2024-08-12 18:30:00', 1, 7, 7, 'MEDIUM', 'OPEN', NULL, NULL, SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC008', 'Equipment Malfunction', 'Elevator stuck between floors', TIMESTAMP '2024-08-06 11:45:00', 1, 9, 8, 'HIGH', 'RESOLVED', 'Elevator repaired and inspected', DATE '2024-08-06', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC009', 'Vehicle Incident', 'Minor fender bender in parking garage', TIMESTAMP '2024-08-05 17:15:00', 1, 5, 9, 'LOW', 'RESOLVED', 'Insurance claims filed, reports completed', DATE '2024-08-05', SYSDATE);
INSERT INTO INCIDENTS VALUES (incidents_seq.NEXTVAL, 'INC010', 'Water Leak', 'Pipe burst in basement storage area', TIMESTAMP '2024-08-04 08:00:00', 1, 10, 10, 'MEDIUM', 'RESOLVED', 'Plumbing repaired, water damage assessed', DATE '2024-08-04', SYSDATE);

-- Insert ACCESS_CARDS (10 rows)
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC001', 1, 'Manager', DATE '2020-01-15', DATE '2025-01-15', 'Level 5', 'ACTIVE', TIMESTAMP '2024-08-12 08:30:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC002', 2, 'Director', DATE '2019-03-20', DATE '2024-12-31', 'Level 5', 'ACTIVE', TIMESTAMP '2024-08-12 09:00:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC003', 3, 'Employee', DATE '2021-06-10', DATE '2026-06-10', 'Level 3', 'ACTIVE', TIMESTAMP '2024-08-12 08:45:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC004', 4, 'Manager', DATE '2020-09-05', DATE '2025-09-05', 'Level 4', 'ACTIVE', TIMESTAMP '2024-08-12 08:00:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC005', 5, 'Employee', DATE '2022-01-12', DATE '2027-01-12', 'Level 2', 'ACTIVE', TIMESTAMP '2024-08-12 09:15:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC006', 6, 'Security', DATE '2018-11-30', DATE '2024-11-30', 'Level 5', 'ACTIVE', TIMESTAMP '2024-08-12 07:30:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC007', 7, 'Manager', DATE '2019-08-22', DATE '2024-08-22', 'Level 4', 'EXPIRING', TIMESTAMP '2024-08-12 08:30:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC008', 8, 'Employee', DATE '2021-04-15', DATE '2026-04-15', 'Level 3', 'ACTIVE', TIMESTAMP '2024-08-12 08:15:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC009', 9, 'Manager', DATE '2020-07-08', DATE '2025-07-08', 'Level 4', 'ACTIVE', TIMESTAMP '2024-08-12 08:45:00', SYSDATE);
INSERT INTO ACCESS_CARDS VALUES (access_cards_seq.NEXTVAL, 'AC010', 10, 'Manager', DATE '2019-12-03', DATE '2024-12-03', 'Level 4', 'ACTIVE', TIMESTAMP '2024-08-12 09:00:00', SYSDATE);

-- Commit all changes
COMMIT;

-- Display summary information
SELECT 'LOCATIONS' TABLE_NAME, COUNT(*) ROW_COUNT FROM LOCATIONS
UNION ALL
SELECT 'DEPARTMENTS', COUNT(*) FROM DEPARTMENTS
UNION ALL
SELECT 'EMPLOYEES', COUNT(*) FROM EMPLOYEES
UNION ALL
SELECT 'SECURITY_GUARDS', COUNT(*) FROM SECURITY_GUARDS
UNION ALL
SELECT 'PROJECTS', COUNT(*) FROM PROJECTS
UNION ALL
SELECT 'GATEPASS', COUNT(*) FROM GATEPASS
UNION ALL
SELECT 'ATTENDANCE', COUNT(*) FROM ATTENDANCE
UNION ALL
SELECT 'VISITORS', COUNT(*) FROM VISITORS
UNION ALL
SELECT 'ASSETS', COUNT(*) FROM ASSETS
UNION ALL
SELECT 'MAINTENANCE', COUNT(*) FROM MAINTENANCE
UNION ALL
SELECT 'TRAINING', COUNT(*) FROM TRAINING
UNION ALL
SELECT 'PAYROLL', COUNT(*) FROM PAYROLL
UNION ALL
SELECT 'INCIDENTS', COUNT(*) FROM INCIDENTS
UNION ALL
SELECT 'ACCESS_CARDS', COUNT(*) FROM ACCESS_CARDS;

select table_name,owner from all_tables;