# Stage 1: Build Angular App
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npx ng build --configuration=production

# Stage 2: Serve with FastAPI
FROM python:3.10-slim
WORKDIR /app

# Copy backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code (including main.py which mounts static files)
COPY backend/ ./backend/

# Copy compiled frontend from Stage 1 to the location expected by main.py
COPY --from=build /app/frontend/dist /app/frontend/dist

# Expose port (Cloud Run uses 8080)
ENV PORT=8080
EXPOSE 8080

# Run FastAPI via Uvicorn
CMD uvicorn backend.main:app --host 0.0.0.0 --port 8080
