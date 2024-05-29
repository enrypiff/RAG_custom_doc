# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

# Set work directory in the container
WORKDIR /app

RUN apt-get update
RUN apt-get install -y sqlite3 libsqlite3-dev

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
CMD ["python", "src/app.py"]