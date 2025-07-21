
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

```
/ai-oracle-chatbot
│
├── backend
│   ├── venv/                  # Python virtual environment
│   ├── main.py                # FastAPI main app
│   ├── ai_handler.py          # Handles AI interactions
│   ├── db_handler.py          # Handles Oracle DB queries
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
│
├── frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API calls
│   │   ├── App.jsx            # Main React component
│   │   └── index.css          # Tailwind CSS imports
│   ├── tailwind.config.js     # Tailwind config
│   └── package.json           # NPM dependencies
│
└── README.md
```

---

## Setup Instructions

### Backend Setup

1. **Create Python Virtual Environment**
```bash
cd backend
python -m venv venv
# Activate on Windows
venv\Scripts\activate
# Activate on Linux/Mac
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install fastapi uvicorn python-dotenv huggingface_hub oracledb
```

3. **Setup Oracle Instant Client (for thick mode)**

- Download from Oracle's official site.
- Extract to a location like `D:\instantclient_23_8`.
- Initialize thick mode in your code:
```python
oracledb.init_oracle_client(lib_dir=r"D:\instantclient_23_8")
```

4. **Create `.env` file in `backend` directory**
```
HF_TOKEN=your_hugging_face_token
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_DSN=localhost/XE
```

5. **Run FastAPI Server**
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. **Initialize Vite React Project**
```bash
npm create vite@latest frontend -- --template react
cd frontend
```

2. **Install Dependencies**
```bash
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

3. **Configure Tailwind in `tailwind.config.js`**
```js
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
```

4. **Add Tailwind Directives in `src/index.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

5. **Run React Dev Server**
```bash
npm run dev
```

---

## Libraries & Technologies

### Backend
- **FastAPI:** Python web framework
- **Uvicorn:** ASGI server
- **python-dotenv:** Load environment variables
- **huggingface_hub:** Access Hugging Face models
- **oracledb:** Oracle DB connectivity

### Frontend
- **React:** UI development
- **Vite:** Frontend tooling
- **Tailwind CSS:** UI styling

### Database
- **Oracle DB:** 11g XE / 19c / 21c XE
- **SQL Developer:** GUI client for Oracle

---

## Usage

1. Start the **backend** FastAPI server.
2. Start the **frontend** React app.
3. Open the frontend in your browser.
4. Input your queries via chat interface.
5. Queries are sent to FastAPI backend which uses Hugging Face API to translate to SQL, executes on Oracle DB, and returns results.
