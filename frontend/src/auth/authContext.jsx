// AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import { loginUser, logoutUser, fetchMe } from "../services/authService";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user already logged in (cookie/session-based)
  // AuthContext.jsx
useEffect(() => {
  const checkAuthStatus = async () => {
    try {
      const me = await fetchMe();
      if (me) {
        setUser(me); // set actual backend user
        setToken({ access_token: "cookie-based" });
      }
    } catch (error) {
      console.error("Auth check failed:", error);
    } finally {
      setIsLoading(false);
    }
  };
  checkAuthStatus();
}, []);

  const login = async (username, password) => {
    console.log("Attempting login with:", username, password);

    const data = await loginUser(username, password);
    if (!data || data.message !== "Login successful") {
      alert("Invalid username or password");
      return null;
    }

    // Backend only returns message + token → create a user object manually
    setUser({ username });
    setToken(data.token);

    console.log("User logged in:", username);
    return username;
  };

  const logout = async () => {
    console.log("Logging out");
    await logoutUser();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
