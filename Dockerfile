# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and .env file
COPY . .
COPY .env .

# Expose the port
EXPOSE 3478

# Set the entrypoint and default command
ENTRYPOINT ["python"]
CMD ["main.py"]