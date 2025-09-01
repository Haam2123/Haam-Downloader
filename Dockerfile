FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Render/Heroku provide $PORT; default to 5000 locally
ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]