import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./authContext";

export default function ProtectedRoute({ children }) {
  const { user, token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user && !token) {
    console.log("Not logged in, redirecting to login page");
    return <Navigate to="/" replace />;
  }

  return children;
}
