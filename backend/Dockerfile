FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Pillow and OCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p assets/fonts assets/images

# Expose the port (FastAPI default or Hugging Face Space default)
EXPOSE 7860

# Run the application (using specific port for HF Spaces if needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
