# Use an official Python runtime as the base image.
FROM python:3.13-alpine

# Set the working directory.
WORKDIR /backend

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY alembic alembic
COPY database database
COPY unit_tests unit_tests
COPY alembic.ini alembic.ini
COPY main.py main.py
COPY endpoints endpoints
COPY test_system test_system
COPY notifications notifications

ENV SECRET_KEY="strong_secret_key"
ENV PASSWORD_RESET_KEY="strong_password_reset_key"
ENV PYTHONUNBUFFERED=1

# Expose the port that the app runs on.
EXPOSE 3000

# Run the application.
CMD ["python", "main.py"]