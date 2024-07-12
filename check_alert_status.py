import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import pytz
import subprocess

def fetch_and_check_status():
    url = "https://kyiv.digital/storage/air-alert/stats.html"  # Replace with the actual URL of your HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the first row of the table
    first_row = soup.select_one('.wrapper table tr')
    if first_row:
        date_cell = first_row.select_one('td:nth-of-type(1)')
        status_cell = first_row.select_one('td:nth-of-type(2)')
        if date_cell and status_cell:
            date_text = date_cell.text.strip()
            status_text = status_cell.text.strip()
            return date_text, status_text

    return None, None

def main():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    current_state_file = 'last_sent_date.txt'

    # Read the last sent date from file
    if os.path.exists(current_state_file):
        with open(current_state_file, 'r') as file:
            last_sent_date_str = file.read().strip()
        last_sent_date = datetime.strptime(last_sent_date_str, '%H:%M %d.%m.%y').replace(tzinfo=kyiv_tz)
    else:
        last_sent_date = None

    # Fetch the current status from the HTML page
    date_str, current_status = fetch_and_check_status()
    print(f"Parsed date/status: {date_str} / {current_status}")

    if date_str and current_status:
        alert_was_over_at = datetime.strptime(date_str, '%H:%M %d.%m.%y').replace(tzinfo=kyiv_tz)
        now = datetime.now(kyiv_tz)

        if "🟢" in current_status:
            # Check if the alert was sent within the last 30 minutes
            if last_sent_date is None or (alert_was_over_at - last_sent_date > timedelta(minutes=30) and alert_was_over_at - now < timedelta(minutes=60)):
                print(f"Alert is over, sending a message")
                # Send a Signal message
                subprocess.run(['/usr/local/bin/python', '/app/send_signal_message.py'])
                # Update the last sent date
                with open(current_state_file, 'w') as file:
                    file.write(alert_was_over_at.strftime('%d.%m.%y %H:%M'))
                print("Message sent successfully")
            else:
                print(f"Not sending a message, last sent: {last_sent_date}, current: {alert_was_over_at}")

if __name__ == "__main__":
    main()
