# Use an official Python runtime as a parent image
FROM python:3.12.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# Define environment variable for the Neptune URL
ENV NEPTUNE_URL=""

# Run app.py when the container launches
CMD ["python", "app.py"]

# build and run docker image
#docker build -t my-neptune-app .
#docker run -p 4000:80 my-neptune-app
