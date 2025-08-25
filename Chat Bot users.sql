-- Drop old table if exists (optional)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

-- Create the table without identity
CREATE TABLE users (
    id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    full_name VARCHAR2(100),
    email VARCHAR2(100) UNIQUE,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Create a sequence for generating IDs
CREATE SEQUENCE users_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Create a BEFORE INSERT trigger to auto-fill the ID from the sequence
CREATE OR REPLACE TRIGGER trg_users_bi
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF :NEW.id IS NULL THEN
        SELECT users_seq.NEXTVAL INTO :NEW.id FROM dual;
    END IF;
END;
/

-- Insert some dummy users (passwords should be hashed in real apps)
INSERT INTO users (username, password_hash, full_name, email)
VALUES ('admin', '$2b$12$hlK7o6QRcaSyG9UUSTGVVOSrxJcgDWfA/e8.dZNl3PSJVuEDUK01u', 'Admin User', 'admin@example.com');

INSERT INTO users (username, password_hash, full_name, email)
VALUES ('testuser', '$2b$12$xwTrWftKNiSD3VnO68kTeOty0OVK12InjIWoNyN3.HPhi2AdFCB2m', 'Test User', 'test@example.com');

COMMIT;


Select * from users;