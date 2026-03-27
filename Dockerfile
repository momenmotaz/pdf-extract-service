# Use an official Python runtime as a parent image (slim for smaller size)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for OCR and Camelot (Ghostscript)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    ghostscript \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install opencv separately first (prone to CRC errors on rolling releases)
RUN pip install --no-cache-dir --retries 5 opencv-python-headless==4.10.0.84

# Install remaining packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the application using Uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
