FROM python:3.12-slim

# Prevents Python from writing pyc files & enables output flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install system dependencies (for psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Django default port
EXPOSE 8000

# Run Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
