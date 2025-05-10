# Use offical Python image as a base image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the dependency file and install package
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]