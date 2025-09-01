import React from "react";
import { Navigate } from "react-router-dom";
import Cookies from "js-cookie";
import { fetchMe } from "../services/authService";

export default function ProtectedRoute({ children }) {
  const token = fetchMe(); // Read cookie

  if (!token) {
    // Not logged in, redirect to login page
    console.log("Not logged in, redirecting to login page");
    return <Navigate to="/" replace />;
  }

  // Logged in, allow access
  return children;
}
