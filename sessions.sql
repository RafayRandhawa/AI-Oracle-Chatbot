-- Table for chat sessions
CREATE TABLE chat_sessions (
    session_id VARCHAR2(36) PRIMARY KEY,
    user_id VARCHAR2(50),
    started_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    last_message_at TIMESTAMP,
    status VARCHAR2(20) DEFAULT 'active'
);

-- Table for messages in each session
CREATE TABLE chat_messages (
    message_id VARCHAR2(36) PRIMARY KEY,
    session_id VARCHAR2(36) REFERENCES chat_sessions(session_id),
    sender VARCHAR2(20),         -- 'user' or 'bot'
    message_text CLOB,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Optional index for faster retrieval of messages per session
CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_created_at ON chat_messages(created_at);

-- Sequence for chat_sessions primary key
CREATE SEQUENCE seq_chat_sessions
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

-- Trigger to auto-assign session_id
CREATE OR REPLACE TRIGGER trg_chat_sessions_pk
BEFORE INSERT ON chat_sessions
FOR EACH ROW
BEGIN
    IF :NEW.session_id IS NULL THEN
        :NEW.session_id := 'S' || TO_CHAR(seq_chat_sessions.NEXTVAL);
    END IF;
END;
/

-- Sequence for chat_messages primary key
CREATE SEQUENCE seq_chat_messages
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

-- Trigger to auto-assign message_id
CREATE OR REPLACE TRIGGER trg_chat_messages_pk
BEFORE INSERT ON chat_messages
FOR EACH ROW
BEGIN
    IF :NEW.message_id IS NULL THEN
        :NEW.message_id := 'M' || TO_CHAR(seq_chat_messages.NEXTVAL);
    END IF;
END;
/

