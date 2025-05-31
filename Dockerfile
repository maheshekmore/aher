# Use official Python image
FROM python:3.11-slim

# Install tesseract and dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-mar && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 10000

# Run the app
CMD ["python", "app.py"]
