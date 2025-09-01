FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Render/Heroku provide $PORT; default to 5000 locally
ENV PORT=5000

EXPOSE 5000

# Run the app with Gunicorn (production-ready)
CMD ["gunicorn", "-b", "0.0.0.0:${PORT}", "app:app"]
