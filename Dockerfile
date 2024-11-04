# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg libnss3 libxss1 libappindicator3-1 libasound2 fonts-liberation \
    libatk-bridge2.0-0 libgtk-3-0 ca-certificates fonts-liberation libu2f-udev && \
    apt-get clean

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb

# Add execute permission to Chrome binary
RUN chmod +x /usr/bin/google-chrome

# Verify Chrome installation
RUN google-chrome --version

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# Set environment variables for Chrome to ensure it works in headless environments
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run your application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
