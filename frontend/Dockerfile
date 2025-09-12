# Frontend Dockerfile for Oracle AI Chatbot
# Multi-stage build for optimized production

# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev, needed for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application (Vite outputs to /app/dist)
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port (Nginx serves frontend on port 80)
EXPOSE 80

# Health check (use root / since React has no /health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
