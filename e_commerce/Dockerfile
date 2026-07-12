# Use an official lightweight Python image
FROM python:3.14-slim

# Set working directory inside the container
WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install dependencies without saving cache files
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the application code
COPY . /app

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
