// ProtectedRoute.jsx
import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./authContext";
import { fetchMe } from "../services/authService";

export default function ProtectedRoute({ children }) {
  const { user, setUser, isLoading } = useAuth(); // we’ll use setUser if needed
  const [verified, setVerified] = useState(null); // null = not checked yet

  useEffect(() => {
    const verifyUser = async () => {
      try {
        // If we already have user in context, no need to fetch again
        if (user) {
          setVerified(true);
          return;
        }

        // Otherwise, check session via backend
        const me = await fetchMe();
        if (me) {
          setUser(me);       // ✅ store user from backend in context
          setVerified(true);
        } else {
          setVerified(false);
        }
      } catch {
        setVerified(false);
      }
    };

    verifyUser();
  }, [user, setUser]);

  if (isLoading || verified === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!verified) {
    console.log("Not logged in, redirecting to login page");
    return <Navigate to="/" replace />;
  }

  return children;
}
