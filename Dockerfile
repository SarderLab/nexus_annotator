# Use an official Python runtime as a parent image
# Using python:3.8-slim as setup.py requires python >= 3.8
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libexpat1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Set the working directory in the container
WORKDIR /app

# Copy the local directory contents into the container at /app
COPY . .

# Install any needed packages specified in setup.py
# This will install packages from 'install_requires' and 'extras_require[interactive]'
RUN pip install --no-cache-dir .[interactive]

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variables
ENV DATABASE_PATH /pubapps/athena/fstools/db


# Run app.py when the container launches
CMD ["python", "app.py"]