# Use an official Python runtime as the base image.
FROM python:3.13-alpine

# Set the working directory.
WORKDIR /frontend

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY main.py main.py

# Expose the port that the app runs on.
EXPOSE 3000

# Run the application.
CMD ["python", "main.py"]