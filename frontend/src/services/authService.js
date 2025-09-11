import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Login (sets cookies on success)
export async function loginUser(username, password) {
  try {
    const res = await axios.post(
      `${API_BASE_URL}/auth/login`,
      { username, password },
      { withCredentials: true,
        validateStatus: () => true
       }
    );
    if(res.status === 401) {
      alert("Invalid username or password");
      return { message: "Login failed" };
    }
    console.log("Login response:", res.data);
    return res.data;
    
  } catch (error) {
    const detail = error?.response?.data?.detail || error?.message || "Login failed";
    throw new Error(detail);
  }
}

// Logout (clears cookies)
export async function logoutUser() {
  await axios.post(
    `${API_BASE_URL}/auth/logout`,
    {},
    { withCredentials: true }
  );
}

// Get current user
export async function fetchMe() {
  try {
    const res = await axios.get(`${API_BASE_URL}/auth/me`, {
      withCredentials: true,
      timeout: 5000, // 5 second timeout
    });
    return res.data?.logged_in === true;
  } catch (error) {
    console.error("Auth check failed:", error);
    return false; 
  }
}

  
