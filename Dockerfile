# Start with a base Python image
FROM python:3.11-slim

#Working directory inside the container
WORKDIR /usr/src/app

#system dependencies needed for the database connector and netcat
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Here we copy the requirements file to the working directory
# and install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the custom entrypoint script and make it executable
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Copy the rest of the application code
COPY . .

# Create the static files directory to resolve the warning
RUN mkdir -p static

# Sets the default command to run the entrypoint script
# The `docker-compose.yml` file will override this
CMD ["sh", "-c", "/usr/src/app/entrypoint.sh"]

# Expose port 8000 for the Django development server
EXPOSE 8000 