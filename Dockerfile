# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies for Selenium and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg libnss3 libxss1 libappindicator3-1 libasound2 fonts-liberation \
    libatk-bridge2.0-0 libgtk-3-0 ca-certificates fonts-liberation libu2f-udev

# Download and extract the Chrome binary
ARG CHROME_VERSION=110.0.5481.77
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+') && \
    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && rm /tmp/chromedriver.zip

# Verify Chrome and ChromeDriver installations
RUN google-chrome --version && chromedriver --version

# Set environment variables to avoid crashes due to insufficient resources
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run your application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
