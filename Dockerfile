FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py seed.py employment_data.py ./
COPY dist/ ./dist/

# Render sets PORT env var
ENV PORT=10000
EXPOSE $PORT

CMD python -m uvicorn server:app --host 0.0.0.0 --port $PORT
