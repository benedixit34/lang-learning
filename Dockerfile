# Use an official Python runtime as a parent image
FROM python:3.12.1

RUN apt-get update && apt-get install -y git && apt-get install -y cron

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN pip install git+https://github.com/SY-2024/drf-stripe-subscription.git

# Copy the entrypoint script and make it executable
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the Django project into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]