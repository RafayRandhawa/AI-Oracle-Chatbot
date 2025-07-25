CREATE USER chatbot_user IDENTIFIED BY chatbotpass;

-- Grant basic privileges
GRANT CONNECT, RESOURCE TO chatbot_user;

-- (Optional) Allow the user to create tables and use unlimited space on their default tablespace
ALTER USER chatbot_user DEFAULT TABLESPACE USERS;
ALTER USER chatbot_user QUOTA UNLIMITED ON USERS;


GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE PROCEDURE TO chatbot_user;

