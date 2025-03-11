# Use the official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy the .env file into the container
# COPY .env .env

EXPOSE 8000


# Create a script to run migrations and start the application
RUN echo "#!/bin/sh" > /app/start.sh && \
    echo "python manage.py makemigrations" >> /app/start.sh && \
    echo "python manage.py migrate" >> /app/start.sh && \
    echo "daphne -b 0.0.0.0 -p 8000 enfund.asgi:application" >> /app/start.sh && \
    chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"]

# Command to run the application using daphne
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "enfund.asgi:application"]