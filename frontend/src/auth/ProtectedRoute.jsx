import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./authContext";

export default function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user) {
    // Not logged in, redirect to login page
    console.log("Not logged in, redirecting to login page");
    return <Navigate to="/" replace />;
  }

  // Logged in, allow access
  return children;
}
