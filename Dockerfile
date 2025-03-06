# Use official Python image as base
FROM python:3.12.1

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (same as Flask app)
EXPOSE 5000

# Define environment variable (optional)
ENV FLASK_APP=main.py

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]