-- Drop tables if they exist
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE gatepasses CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE vehicles CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE security_guards CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE departments CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

-- Create tables
CREATE TABLE departments (
    dept_id     NUMBER PRIMARY KEY,
    dept_name   VARCHAR2(100) NOT NULL UNIQUE
);

CREATE TABLE vehicles (
    vehicle_id      NUMBER PRIMARY KEY,
    plate_number    VARCHAR2(20) NOT NULL UNIQUE,
    vehicle_type    VARCHAR2(50),
    color           VARCHAR2(30),
    dept_id         NUMBER REFERENCES departments(dept_id)
);

CREATE TABLE security_guards (
    guard_id    NUMBER PRIMARY KEY,
    guard_name  VARCHAR2(100) NOT NULL,
    shift       VARCHAR2(20),
    contact_no  VARCHAR2(20)
);

CREATE TABLE gatepasses (
    pass_id         NUMBER PRIMARY KEY,
    vehicle_id      NUMBER REFERENCES vehicles(vehicle_id),
    issued_by       VARCHAR2(100),
    issued_to       VARCHAR2(100),
    purpose         VARCHAR2(255),
    issue_date      DATE DEFAULT SYSDATE,
    return_date     DATE,
    guard_id        NUMBER REFERENCES security_guards(guard_id),
    status          VARCHAR2(20) CHECK (status IN ('Approved', 'Pending', 'Cancelled'))
);

-- Create sequences
CREATE SEQUENCE seq_dept START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_vehicle START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_guard START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_pass START WITH 1 INCREMENT BY 1;

-- Insert sample data
-- Departments
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'IT');
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'HR');
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'Logistics');

-- Vehicles
INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'ABC-123', 'Car', 'White', 1);

INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'XYZ-789', 'Van', 'Blue', 2);

-- Security Guards
INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Ali Khan', 'Morning', '03001234567');

INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Zara Sheikh', 'Night', '03007654321');

-- Gatepasses
INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 1, 'Manager IT', 'Vendor A', 'Laptop delivery', SYSDATE + 2, 1, 'Approved');

INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 2, 'HR Officer', 'Recruitment Team', 'Interview event', SYSDATE + 1, 2, 'Pending');


INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'Finance');
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'Administration');
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'Engineering');
INSERT INTO departments (dept_id, dept_name) VALUES (seq_dept.NEXTVAL, 'Procurement');

INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'JKL-555', 'Truck', 'Red', 3);

INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'GHI-432', 'Motorcycle', 'Black', 4);

INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'LMN-888', 'Car', 'Silver', 5);

INSERT INTO vehicles (vehicle_id, plate_number, vehicle_type, color, dept_id)
VALUES (seq_vehicle.NEXTVAL, 'PQR-999', 'SUV', 'Green', 6);

INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Imran Abbas', 'Evening', '03001112222');

INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Maira Khan', 'Morning', '03002223333');

INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Bilal Sheikh', 'Night', '03003334444');

INSERT INTO security_guards (guard_id, guard_name, shift, contact_no)
VALUES (seq_guard.NEXTVAL, 'Sana Javed', 'Evening', '03004445555');




INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 3, 'Logistics Manager', 'Vendor B', 'Material transport', SYSDATE + 3, 3, 'Approved');

INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 4, 'Admin Officer', 'Courier Service', 'Document delivery', SYSDATE + 1, 4, 'Cancelled');

INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 5, 'Finance Head', 'Auditor Team', 'Audit Visit', SYSDATE + 2, 5, 'Pending');

INSERT INTO gatepasses (pass_id, vehicle_id, issued_by, issued_to, purpose, return_date, guard_id, status)
VALUES (seq_pass.NEXTVAL, 6, 'Engineer Lead', 'Maintenance Crew', 'Repair Work', SYSDATE + 5, 6, 'Approved');



-- Sequence for employees
CREATE SEQUENCE seq_employee START WITH 1 INCREMENT BY 1;

-- Employees table
CREATE TABLE employees (
    emp_id         NUMBER PRIMARY KEY,
    emp_name       VARCHAR2(100) NOT NULL,
    designation    VARCHAR2(100),
    contact_no     VARCHAR2(20),
    dept_id        NUMBER NOT NULL,
    vehicle_id     NUMBER, -- optional: not every employee may have a vehicle
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);


-- Employee 1 - Linked to IT (1), Car (1)
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Ali Raza', 'Software Engineer', '03001110001', 1, 1);

-- Employee 2 - Linked to HR (2), Van (2)
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Sara Khan', 'HR Manager', '03002220002', 2, 2);

-- Employee 3 - Linked to Engineering (5), Truck (3)
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Usman Tariq', 'Field Engineer', '03003330003', 5, 3);

-- Employee 4 - Linked to Procurement (6), SUV (6)
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Ayesha Malik', 'Procurement Officer', '03004440004', 6, 6);

-- Employee 5 - Linked to Finance (3), no vehicle
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Zain Ul Abideen', 'Accountant', '03005550005', 3, NULL);

-- Employee 6 - Linked to Admin (4), Motorcycle (4)
INSERT INTO employees (emp_id, emp_name, designation, contact_no, dept_id, vehicle_id)
VALUES (seq_employee.NEXTVAL, 'Hira Yousuf', 'Admin Assistant', '03006660006', 4, 4);






--Testing
SELECT e.emp_id, e.emp_name, d.dept_name dept_name, v.plate_number vehicle_plate_number FROM employees e JOIN departments d ON e.dept_id = d.dept_id LEFT JOIN vehicles v ON e.vehicle_id = v.vehicle_id;

commit;
