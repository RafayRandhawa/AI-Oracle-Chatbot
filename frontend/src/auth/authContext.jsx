// AuthContext.jsx
import React, { createContext, useState } from "react";

// Create the AuthContext to share auth state globally
export const AuthContext = createContext();

// Provider component to wrap the entire app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);   // Stores user data
  const [token, setToken] = useState(null); // Stores JWT token

  // Login function - stores user and token
  const login = (username, token) => {
    setUser({ username });
    setToken(token);
    localStorage.setItem("token", token); // Persist token across refreshes
  };

  // Logout function - clears stored data
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
