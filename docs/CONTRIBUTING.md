# Development Workflow and Contribution Guidelines

## Overview

This document outlines the development workflow, coding standards, and contribution guidelines for the Oracle AI Chatbot project. It provides comprehensive guidance for developers, contributors, and maintainers.

---

## 🚀 Getting Started

### Prerequisites

**Required Software:**
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.30+)
- **Node.js** (18+) and **npm** (8+)
- **Python** (3.11+)
- **Oracle Database** (11g XE, 19c, or 21c XE)
- **Oracle Instant Client** (21.13+)

**Development Tools:**
- **VS Code** (recommended) with extensions:
  - Python
  - JavaScript/TypeScript
  - Docker
  - GitLens
  - Prettier
  - ESLint

### Initial Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/ai-oracle-chatbot.git
cd ai-oracle-chatbot
```

2. **Set up development environment:**
```bash
# Copy environment templates
cp env.example .env
cp frontend/env.example frontend/.env

# Edit configuration files
# Update database credentials, API keys, etc.
```

3. **Start development services:**
```bash
# Start all services
docker-compose up -d

# Or start specific services
docker-compose up -d backend frontend
```

4. **Verify setup:**
```bash
# Check service health
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000/health
```

---

## 🏗️ Development Workflow

### Branch Strategy

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features
- `release/*` - Release preparation branches
- `hotfix/*` - Critical bug fixes

**Feature Branches:**
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Development Process

1. **Create Feature Branch:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/new-chat-feature
```

2. **Development Work:**
```bash
# Make changes
# Write tests
# Update documentation
# Test locally
```

3. **Commit Changes:**
```bash
git add .
git commit -m "feat: add new chat feature

- Implement new chat functionality
- Add message validation
- Update UI components
- Add unit tests

Closes #123"
```

4. **Push and Create PR:**
```bash
git push origin feature/new-chat-feature
# Create Pull Request on GitHub
```

### Commit Message Convention

**Format:**
```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add JWT token refresh functionality

- Implement token refresh endpoint
- Add automatic token renewal
- Update frontend auth service
- Add unit tests for token refresh

Closes #456

fix(chat): resolve message persistence issue

- Fix database connection handling
- Update session management
- Add error logging
- Improve error messages

Fixes #789
```

---

## 🧪 Testing Strategy

### Testing Framework

**Backend Testing:**
- **pytest** - Python testing framework
- **pytest-asyncio** - Async testing support
- **httpx** - HTTP client for API testing
- **pytest-cov** - Coverage reporting

**Frontend Testing:**
- **Jest** - JavaScript testing framework
- **React Testing Library** - React component testing
- **Cypress** - End-to-end testing
- **MSW** - API mocking

### Test Structure

```
tests/
├── backend/
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_db_handler.py
│   │   └── test_ai_handler.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   └── test_database_integration.py
│   └── e2e/
│       └── test_complete_workflow.py
├── frontend/
│   ├── unit/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/
│   │   └── test_api_integration.js
│   └── e2e/
│       └── test_user_workflows.js
└── shared/
    ├── fixtures/
    └── helpers/
```

### Running Tests

**Backend Tests:**
```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/unit/test_auth_service.py

# Run with coverage
docker-compose exec backend pytest --cov=backend --cov-report=html

# Run integration tests
docker-compose exec backend pytest tests/integration/
```

**Frontend Tests:**
```bash
# Run unit tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm test -- --coverage

# Run e2e tests
docker-compose exec frontend npm run test:e2e
```

**All Tests:**
```bash
# Run complete test suite
docker-compose exec backend pytest
docker-compose exec frontend npm test
docker-compose exec frontend npm run test:e2e
```

### Test Coverage Requirements

**Minimum Coverage:**
- **Backend**: 80% code coverage
- **Frontend**: 75% code coverage
- **Critical Paths**: 90% coverage (auth, database, AI)

**Coverage Reports:**
```bash
# Generate coverage reports
docker-compose exec backend pytest --cov=backend --cov-report=html
docker-compose exec frontend npm test -- --coverage

# View reports
open backend/htmlcov/index.html
open frontend/coverage/lcov-report/index.html
```

---

## 📝 Code Standards

### Python (Backend)

**Style Guide:** PEP 8 with Black formatting

**Configuration:**
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

**Code Formatting:**
```bash
# Format code
docker-compose exec backend black .
docker-compose exec backend isort .

# Check formatting
docker-compose exec backend black --check .
docker-compose exec backend isort --check-only .
```

**Type Hints:**
```python
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

def process_messages(
    messages: List[Dict[str, str]], 
    session_id: Optional[int] = None
) -> Dict[str, Union[str, int]]:
    """Process chat messages with type hints."""
    pass
```

**Documentation:**
```python
def generate_sql_from_prompt(prompt: str) -> str:
    """
    Generate SQL query from natural language prompt.
    
    Args:
        prompt: User's natural language query
        
    Returns:
        Generated SQL query string
        
    Raises:
        ValueError: If prompt is empty or invalid
        AIException: If AI service fails
        
    Example:
        >>> generate_sql_from_prompt("Show me all users")
        "SELECT * FROM users"
    """
    pass
```

### JavaScript/React (Frontend)

**Style Guide:** ESLint + Prettier

**Configuration:**
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

**Code Formatting:**
```bash
# Format code
docker-compose exec frontend npm run lint:fix
docker-compose exec frontend npm run format

# Check formatting
docker-compose exec frontend npm run lint
```

**Component Structure:**
```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * ChatUI component for displaying chat interface
 * @param {Object} props - Component props
 * @param {Array} props.messages - Array of chat messages
 * @param {Function} props.setMessages - Function to update messages
 * @param {string} props.currentSessionId - Current session ID
 * @param {Function} props.setCurrentSessionId - Function to update session ID
 */
export default function ChatUI({ 
  messages, 
  setMessages, 
  currentSessionId, 
  setCurrentSessionId 
}) {
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  // Component logic here

  return (
    <div className="chat-container">
      {/* Component JSX */}
    </div>
  );
}

ChatUI.propTypes = {
  messages: PropTypes.array.isRequired,
  setMessages: PropTypes.func.isRequired,
  currentSessionId: PropTypes.string,
  setCurrentSessionId: PropTypes.func.isRequired,
};
```

### Database Standards

**SQL Style:**
```sql
-- Use uppercase for keywords
-- Use lowercase for identifiers
-- Use descriptive names
-- Include comments for complex queries

-- Example: Get active employees with department info
SELECT 
    e.emp_id,
    e.first_name,
    e.last_name,
    e.email,
    d.dept_name,
    e.salary
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id
WHERE e.status = 'ACTIVE'
  AND e.hire_date >= DATE '2020-01-01'
ORDER BY e.last_name, e.first_name;
```

**Migration Scripts:**
```sql
-- Migration: Add new column to users table
-- Version: 2024.01.09.001
-- Description: Add last_login column to track user activity

ALTER TABLE users ADD last_login TIMESTAMP;

-- Add index for performance
CREATE INDEX idx_users_last_login ON users(last_login);

-- Update existing records
UPDATE users SET last_login = created_at WHERE last_login IS NULL;
```

---

## 🔧 Development Tools

### VS Code Configuration

**Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "**/.git": true
  }
}
```

**Extensions (.vscode/extensions.json):**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-azuretools.vscode-docker"
  ]
}
```

### Git Hooks

**Pre-commit Hook (.git/hooks/pre-commit):**
```bash
#!/bin/bash
# Run tests and linting before commit

echo "Running pre-commit checks..."

# Backend checks
docker-compose exec backend black --check .
if [ $? -ne 0 ]; then
    echo "Backend formatting failed. Run 'black .' to fix."
    exit 1
fi

docker-compose exec backend pytest tests/unit/
if [ $? -ne 0 ]; then
    echo "Backend tests failed."
    exit 1
fi

# Frontend checks
docker-compose exec frontend npm run lint
if [ $? -ne 0 ]; then
    echo "Frontend linting failed."
    exit 1
fi

echo "All checks passed!"
```

### Docker Development

**Development Docker Compose (docker-compose.dev.yml):**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
      - /app/venv  # Exclude venv from volume mount
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Exclude node_modules from volume mount
    environment:
      - NODE_ENV=development
    command: npm run dev
```

---

## 📚 Documentation Standards

### Code Documentation

**Python Docstrings:**
```python
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user credentials against database.
    
    Args:
        username: User's login username
        password: User's plain text password
        
    Returns:
        User data dictionary if authentication successful, None otherwise
        
    Raises:
        DatabaseError: If database connection fails
        ValidationError: If credentials are invalid format
        
    Example:
        >>> user = authenticate_user("john_doe", "password123")
        >>> if user:
        ...     print(f"Welcome {user['first_name']}")
    """
    pass
```

**JavaScript JSDoc:**
```javascript
/**
 * Sends message to N8N workflow for AI processing
 * @param {string} userMessage - The user's message content
 * @param {Object} token - Authentication token object
 * @param {string} token.access_token - JWT access token
 * @returns {Promise<string>} AI-generated response
 * @throws {Error} If API request fails
 * @example
 * const response = await sendToN8n("Show me all users", {access_token: "jwt_token"});
 * console.log(response);
 */
export async function sendToN8n(userMessage, token) {
  // Implementation
}
```

### API Documentation

**OpenAPI/Swagger Documentation:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class QueryRequest(BaseModel):
    """Request model for SQL query generation."""
    prompt: str
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Show me all employees in the IT department"
            }
        }

@app.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    """
    Generate SQL query from natural language prompt.
    
    This endpoint takes a natural language prompt and returns a generated
    SQL query along with its execution results.
    
    - **prompt**: Natural language description of the desired query
    
    Returns:
    - **generated_sql**: The generated SQL query
    - **results**: Query execution results
    """
    pass
```

---

## 🚀 Deployment Process

### Development Deployment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Check logs
docker-compose logs -f
```

### Staging Deployment

```bash
# Deploy to staging
git checkout develop
git pull origin develop
docker-compose -f docker-compose.staging.yml up -d --build

# Run integration tests
docker-compose exec backend pytest tests/integration/
docker-compose exec frontend npm run test:e2e

# Health check
curl http://staging.your-domain.com/health
```

### Production Deployment

```bash
# Create release branch
git checkout develop
git checkout -b release/v1.2.0
git push origin release/v1.2.0

# Deploy to production
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🤝 Contributing Process

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes with tests**
4. **Update documentation**
5. **Run full test suite**
6. **Create pull request**

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No breaking changes

## Related Issues
Closes #123
```

### Code Review Process

**Review Criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Security considerations
- Breaking changes

**Review Checklist:**
- [ ] Code follows project standards
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] No breaking changes without notice

---

## 📊 Performance Guidelines

### Backend Performance

**Database Optimization:**
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

# Optimize queries
def get_user_sessions(user_id: int) -> List[Dict]:
    """Optimized query with proper indexing."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use parameterized queries
    cursor.execute(
        "SELECT id, title, started_at FROM chat_sessions WHERE user_id = :1",
        (user_id,)
    )
    
    return [{"id": row[0], "title": row[1], "started_at": row[2]} 
            for row in cursor.fetchall()]
```

**Caching Strategy:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_database_metadata(force_refresh: bool = False) -> Dict:
    """Cache database metadata for performance."""
    pass
```

### Frontend Performance

**Component Optimization:**
```jsx
import React, { memo, useCallback, useMemo } from 'react';

const ChatMessage = memo(({ message, onEdit }) => {
  const formattedDate = useMemo(() => 
    new Date(message.created_at).toLocaleString(), 
    [message.created_at]
  );
  
  const handleEdit = useCallback(() => {
    onEdit(message.id);
  }, [message.id, onEdit]);
  
  return (
    <div className="message">
      <span>{message.content}</span>
      <span>{formattedDate}</span>
      <button onClick={handleEdit}>Edit</button>
    </div>
  );
});
```

**Bundle Optimization:**
```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};
```

---

## 🔒 Security Guidelines

### Backend Security

**Input Validation:**
```python
from pydantic import BaseModel, validator
import re

class LoginRequest(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Invalid username format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v
```

**SQL Injection Prevention:**
```python
def execute_query(query: str, params: Dict[str, Any]) -> List[Dict]:
    """Execute query with parameter binding."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use parameterized queries
    cursor.execute(query, params)
    return cursor.fetchall()
```

### Frontend Security

**XSS Prevention:**
```jsx
import DOMPurify from 'dompurify';

const MessageContent = ({ content }) => {
  const sanitizedContent = useMemo(() => 
    DOMPurify.sanitize(content), 
    [content]
  );
  
  return (
    <div 
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
    />
  );
};
```

**CSRF Protection:**
```javascript
// Include CSRF token in requests
const apiCall = async (url, data) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken,
    },
    body: JSON.stringify(data),
  });
};
```

---

## 📚 Additional Resources

### Learning Resources

- [Python Best Practices](https://docs.python-guide.org/)
- [React Best Practices](https://react.dev/learn)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Oracle Database Documentation](https://docs.oracle.com/en/database/)

### Tools and Extensions

- [Black Code Formatter](https://black.readthedocs.io/)
- [Prettier Code Formatter](https://prettier.io/)
- [ESLint JavaScript Linter](https://eslint.org/)
- [Pytest Testing Framework](https://pytest.org/)
- [Jest Testing Framework](https://jestjs.io/)

### Community

- [GitHub Discussions](https://github.com/your-org/ai-oracle-chatbot/discussions)
- [Discord Server](https://discord.gg/your-server)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/oracle-ai-chatbot)

---

**Happy Coding! 🚀**

