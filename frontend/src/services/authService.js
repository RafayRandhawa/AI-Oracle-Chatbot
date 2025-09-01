import axios from "axios";

// Login (sets cookies on success)
export async function loginUser(username, password) {
  try {
    const res = await axios.post(
      "http://localhost:8000/auth/login",
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
    "http://localhost:8000/auth/logout",
    {},
    { withCredentials: true }
  );
}

// Get current user
export async function fetchMe() {
  try {
    const res = await axios.get("http://localhost:8000/auth/me", {
      withCredentials: true,
    });
    return res.data?.logged_in === true;
  } catch {
    return false; 
  }
}

  
