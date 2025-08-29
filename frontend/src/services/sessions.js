import axios from "axios";

// Create a new session
export async function createSession(title) {
  try {
    console.log("Making createSession request with title:", title);

    const res = await axios.post(
      "http://localhost:8000/sessions/create-session",
      { title },
      { withCredentials: true }
    );

    console.log("createSession response:", res.data);
    return res.data;
  } catch (error) {
    console.error("createSession error:", error);
    console.error("Error response:", error.response);

    const detail =
      error?.response?.data?.detail || error?.message || "Failed to create session";
    throw new Error(detail);
  }
}

// Get all sessions
export async function getSessions() {
  try {
    const res = await axios.get("http://localhost:8000/sessions/get-sessions", {
      withCredentials: true,
    });
    console.log(res.data["sessions"]);
    return res.data["sessions"] || [];
  } catch (error) {
    const detail =
      error?.response?.data?.detail || error?.message || "Failed to fetch sessions";
    throw new Error(detail);
  }
}

// Get all messages for a session
export async function getMessages(sessionId) {
  try {
    const res = await axios.get(
      `http://localhost:8000/sessions/get-messages/${sessionId}`,
      { withCredentials: true }
    );
    return res.data["messages"] || [];
  } catch (error) {
    const detail =
      error?.response?.data?.detail || error?.message || "Failed to fetch messages";
    throw new Error(detail);
  }
}

// Store a message
export async function storeMessages(sessionId, message) {
  const content = {
    session_id: sessionId,
    role: message.role,
    content: message.content,
  };

  try {
    const res = await axios.post(
      `http://localhost:8000/sessions/set-messages/${sessionId}`,
      content,
      { withCredentials: true }
    );
    return res.data;
  } catch (error) {
    const detail =
      error?.response?.data?.detail || error?.message || "Failed to store messages";
    throw new Error(detail);
  }
}

/*export async function storeMessages(sessionId, message) {
  const payload = {
    session_id: sessionId,
    role: message.role,
    content: message.content,
    model: message.model || null,
    prompt_tokens: message.prompt_tokens || null,
    completion_tokens: message.completion_tokens || null,
    latency_ms: message.latency_ms || null,
    sql_text: message.sql_text || null,
    sql_blocked: message.sql_blocked ?? 0,   // default 0
    error_text: message.error_text || null,
  };

  try {
    const res = await axios.post(
      "http://localhost:8000/sessions/set-messages",
      payload,
      { withCredentials: true }
    );
    return res.data;
  } catch (error) {
    const detail =
      error?.response?.data?.detail ||
      error?.message ||
      "Failed to store messages";
    throw new Error(detail);
  }
}
*/
