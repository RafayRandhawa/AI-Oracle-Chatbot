import axios from "axios";

//const API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://10.0.1.74:8000";

// Login (sets cookies on success)
export async function loginUser(username, password) {
  console.log("API BASE URL:", import.meta.env.VITE_API_URL);
  try {
    const res = await axios.post(
      `${API_BASE_URL}/auth/login`,
      { username, password },
      {
        withCredentials: true,
        validateStatus: () => true,
      }
    );

    if (res.status === 401) {
      alert("Invalid username or password");
      return { success: false, message: "Login failed" };
    }

    if (res.status >= 200 && res.status < 300) {
      console.log("Login response:", res.data);
      return { success: true, ...res.data };
    }

    return { success: false, message: res.data?.detail || "Login failed" };
  } catch (error) {
    const detail =
      error?.response?.data?.detail || error?.message || "Login failed";
    return { success: false, message: detail };
  }
}

// Logout (clears cookies)
export async function logoutUser() {
  try {
    await axios.post(
      `${API_BASE_URL}/auth/logout`,
      {},
      { withCredentials: true }
    );
    return { success: true };
  } catch (error) {
    console.error("Logout failed:", error);
    return { success: false };
  }
}

// Get current user
// authService.js
export async function fetchMe() {
  try {
    const res = await axios.get(`${API_BASE_URL}/auth/me`, {
      withCredentials: true,
      timeout: 5000,
    });

    // Expecting backend to return { logged_in: true, user: {...} }
    if (res.data?.logged_in) {
      return res.data.user; // return full user object
    }
    return null;
  } catch (error) {
    console.error("Auth check failed:", error);
    return null;
  }
}

