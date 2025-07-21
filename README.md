# AI-Oracle-Chatbot

## Project Overview

The AI-Oracle-Chatbot is a full-stack web application designed to translate natural language queries into SQL, execute them against an Oracle Database, and return structured, human-readable results. This solution integrates a React frontend, a FastAPI backend, and Hugging Face models for AI-driven SQL generation.

---

## Features

- **Natural Language to SQL Translation**
- **Oracle Database Query Execution**
- **React + Vite Frontend**
- **FastAPI Backend**
- **Hugging Face API for AI SQL Generation**
- **Styled using Tailwind CSS**

---

## Project Structure

/ai-oracle-chatbot
│
├── backend
│ ├── venv/ # Python virtual environment
│ ├── main.py # FastAPI main app
│ ├── ai_handler.py # Handles AI interactions
│ ├── db_handler.py # Handles Oracle DB queries
│ ├── .env # Environment variables
│ └── requirements.txt # Python dependencies
│
├── frontend
│ ├── public/
│ ├── src/
│ │ ├── components/ # React components
│ │ ├── services/ # API calls
│ │ ├── App.jsx # Main React component
│ │ └── index.css # Tailwind CSS imports
│ ├── tailwind.config.js # Tailwind config
│ └── package.json # NPM dependencies
│
└── README.md

yaml
Copy
Edit

---

## Setup Instructions

### Backend Setup

1. **Create Python Virtual Environment**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
Install Dependencies

bash
Copy
Edit
pip install fastapi uvicorn python-dotenv huggingface_hub oracledb
Setup Oracle Instant Client (for thick mode)

Download the Oracle Instant Client from Oracle's official site.

Extract it to a location e.g., D:\instantclient_23_8.

Initialize thick mode in your code:

python
Copy
Edit
oracledb.init_oracle_client(lib_dir=r"D:\instantclient_23_8")
Create .env file in the backend directory:

ini
Copy
Edit
HF_TOKEN=your_hugging_face_token
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_DSN=localhost/XE
Run the FastAPI Server:

bash
Copy
Edit
uvicorn main:app --reload
Frontend Setup
Initialize Vite React Project

bash
Copy
Edit
npm create vite@latest frontend -- --template react
cd frontend
Install Dependencies

bash
Copy
Edit
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
Configure Tailwind in tailwind.config.js

js
Copy
Edit
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
Add Tailwind Directives in src/index.css

css
Copy
Edit
@tailwind base;
@tailwind components;
@tailwind utilities;
Run React Dev Server:

bash
Copy
Edit
npm run dev
Libraries & Technologies
Backend
FastAPI: Python web framework for the API.

Uvicorn: ASGI server for FastAPI.

python-dotenv: Loads environment variables.

huggingface_hub: For accessing Hugging Face models.

oracledb: Python package for Oracle DB connectivity.

Frontend
React: Frontend library.

Vite: Modern build tool.

Tailwind CSS: For UI styling.

Oracle DB
Oracle 11g XE / 19c / 21c XE

SQL Developer: For database interaction.

Usage
Start the backend FastAPI server.

Start the frontend React app.

Open the frontend UI to interact with the chatbot.

The chatbot sends queries to FastAPI, which uses Hugging Face to translate natural language to SQL, then executes the query on Oracle DB.

