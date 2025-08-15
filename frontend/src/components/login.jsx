// src/components/Login.jsx
import React, { useState } from "react";
import { useTheme } from "./theme-context";
import { useAuth } from "../auth/authContext";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const { theme } = useTheme();
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const user = await login(username, password);
    if (user) {
      navigate("/chat");
    } else {
      alert("Invalid credentials");
    }
  };

  const containerClasses = `flex flex-col items-center justify-center min-h-screen ${
    theme === "dark" ? "bg-[#121212] text-white" : "bg-white text-black"
  }`;

  const inputClasses = `w-full px-4 py-2 rounded-lg border focus:outline-none ${
    theme === "dark"
      ? "bg-[#1E1E1E] border-gray-600 text-white placeholder-gray-400"
      : "bg-white border-gray-300 text-black placeholder-gray-500"
  }`;

  const buttonClasses = `w-full py-2 rounded-lg font-semibold transition-colors ${
    theme === "dark"
      ? "bg-[#D32F2F] hover:bg-red-700 text-white"
      : "bg-red-600 hover:bg-red-700 text-white"
  }`;

  return (
    <div className={containerClasses}>
      <div
        className={`w-full max-w-md p-8 rounded-lg shadow-lg ${
          theme === "dark" ? "bg-[#1E1E1E]" : "bg-gray-200"
        }`}
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block mb-1">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              className={inputClasses}
            />
          </div>

          <div>
            <label htmlFor="password" className="block mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              className={inputClasses}
            />
          </div>

          <button type="submit" className={buttonClasses}>
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
