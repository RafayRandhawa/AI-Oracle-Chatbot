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
    const detail = error?.response?.data?.detail || error?.message || "Failed to create session";
    throw new Error(detail);
  }
}

export async function getSessions() {
  try {
    const res = await axios.get("http://localhost:8000/sessions/get-sessions", {
      withCredentials: true,
    });
    return res.data['sessions'] || [];
  } catch (error) {
    const detail = error?.response?.data?.detail || error?.message || "Failed to fetch sessions";
    throw new Error(detail);
  }
}

export async function getMessages(sessionId) {
  try {
    const res = await axios.get(`http://localhost:8000/sessions/get-messages/${sessionId}`, {
      withCredentials: true,
    });
    return res.data['messages'] || [];
  } catch (error) {
    const detail = error?.response?.data?.detail || error?.message || "Failed to fetch messages";
    throw new Error(detail);
  }
}