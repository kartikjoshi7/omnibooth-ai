# Stage 1: Build Angular App
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build --configuration=production

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

# Expose port (Cloud Run sets PORT env variable)
ENV PORT=8000
EXPOSE $PORT

# Run FastAPI via Uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]
