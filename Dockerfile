# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Java (required for Signal-CLI) and cron
RUN apt-get update && apt-get install -y default-jre wget cron

# Download Signal-CLI
RUN wget https://github.com/AsamK/signal-cli/releases/download/v0.13.4/signal-cli-0.13.4.tar.gz
RUN sudo tar xf signal-cli-0.13.4.tar.gz -C /opt
RUN sudo ln -sf /opt/signal-cli-0.13.4/bin/signal-cli /usr/local/bin/

# Install OpenJDK 17 (required for Signal-CLI) and cron
RUN apt-get update && \
    apt-get install -y wget cron && \
    sudo apt install openjdk-21-jre

# Ensure the script is executable
RUN chmod +x /app/check_alert_status.py
RUN chmod +x /app/send_signal_message.py

# Add the crontab file
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
