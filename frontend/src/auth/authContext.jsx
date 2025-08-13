// AuthContext.jsx
import React, { createContext, useEffect, useState, useCallback } from "react";
import axios from "axios";

// Create a context to share auth state & functions across the app
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Store the currently logged-in user's info (null if not logged in)
  const [user, setUser] = useState(null);
  // Track an auth-loading state to prevent UI flicker
  const [loading, setLoading] = useState(true);

  /**
   * Fetch the current user using the access token cookie.
   * - The backend reads the access token from an HTTP-only cookie
   * - We must send fetch with credentials: "include" so cookies go along
   */
  const fetchMe = useCallback(async () => {
    try {
      const res = await axios.get("http://localhost:8000/auth/me", {
        withCredentials: true,
      });
      setUser(res.data?.user ?? null);
    } catch (e) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Attempt silent refresh if /auth/me fails due to expired access token
   * - Calls /auth/refresh to rotate access token using refresh cookie
   */
  const refresh = useCallback(async () => {
    try {
      await axios.post(
        "http://localhost:8000/auth/refresh",
        {},
        { withCredentials: true }
      );
      return true;
    } catch {
      return false;
    }
  }, []);

  /**
   * Login with username + password
   * - Backend sets HTTP-only cookies for access + refresh tokens
   * - Returns user profile; we store only user in memory state
   */
  const login = useCallback(async (username, password) => {
    try {
      const res = await axios.post(
        "http://localhost:8000/auth/login",
        { username, password },
        { withCredentials: true }
      );
      const userData = res.data?.user;
      setUser(userData);
      return userData;
    } catch (error) {
      const detail = error?.response?.data?.detail || error?.message || "Login failed";
      throw new Error(detail);
    }
  }, []);

  /**
   * Logout
   * - Backend clears the cookies
   * - We clear in-memory user state
   */
  const logout = useCallback(async () => {
    await axios.post(
      "http://localhost:8000/auth/logout",
      {},
      { withCredentials: true }
    );
    setUser(null);
  }, []);

  /**
   * On mount:
   * - Try to get current user via /auth/me
   * - If access token expired, try /auth/refresh, then retry /auth/me
   */
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const meRes = await axios.get("http://localhost:8000/auth/me", {
          withCredentials: true,
        });
        setUser(meRes.data?.user ?? null);
        setLoading(false);
        return;
      } catch {}

      // Try refresh
      const refreshed = await refresh();
      if (refreshed) {
        await fetchMe();
      } else {
        setUser(null);
        setLoading(false);
      }
    })();
  }, [fetchMe, refresh]);

  const value = { user, loading, login, logout, refresh, fetchMe };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
