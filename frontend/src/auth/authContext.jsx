// AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import { loginUser, logoutUser, fetchMe } from "../services/authService";
// Create the AuthContext to share auth state globally
export const AuthContext = createContext();

// Provider component to wrap the entire app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);   // Stores user data
  const [token, setToken] = useState(null); // Stores JWT token
  const [isLoading, setIsLoading] = useState(true); // Loading state

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const isLoggedIn = await fetchMe();
        if (isLoggedIn) {
          // User is logged in, but we don't have token in state
          // The token is stored in cookies by the backend
          setUser({ username: "User" }); // Set a default user object
          setToken({ access_token: "cookie-based" }); // Indicate token is in cookies
        }
      } catch (error) {
        console.error("Auth check failed:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Login function - stores user and token
  const login = async (email, password) => {
    console.log("Attempting login with:", email, password);
    
    const data = await loginUser(email, password);
    if (!data || data.message !== "Login successful") {
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