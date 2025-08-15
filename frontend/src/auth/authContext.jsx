// AuthContext.jsx
import React, { createContext, useState,useContext } from "react";
import { loginUser } from "../services/authService";
// Create the AuthContext to share auth state globally
export const AuthContext = createContext();

// Provider component to wrap the entire app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);   // Stores user data
  const [token, setToken] = useState(null); // Stores JWT token

  // Login function - stores user and token
  const login = async (email, password) => {
    console.log("Attempting login with:", email, password);
    
    const data = await loginUser(email, password);
    if (!data || data.message != "Login successful") {
      throw new Error("Invalid response from server");
    }
    if(data && data.message === "Login Failed") {
      alert("Invalid username or password");
      return null; // Return null if login fails
    }
    setUser(data.user);       // Save user data
    setToken(data.token); // Save JWT token
    console.log("User logged in:", email);
    
    return email;
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

export const useAuth = () => useContext(AuthContext);