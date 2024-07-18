import os
import csv
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

# Create Twilio client
client = Client(account_sid, auth_token)

# Set date range
start_date = datetime(datetime.now().year, 6, 1)  # June 1st of current year
end_date = datetime.now()  # Today

# Prepare CSV file
csv_filename = 'twilio_sms_export.csv'
csv_headers = ['Date Sent', 'From', 'To', 'Body']

# Function to fetch messages in chunks
def fetch_messages(start_date, end_date, chunk_size=1000):
    page = client.messages.list(date_sent_after=start_date, date_sent_before=end_date, limit=chunk_size)
    yield from page

    while page:
        last_message = page[-1]
        page = client.messages.list(date_sent_after=start_date, date_sent_before=last_message.date_sent, limit=chunk_size)
        if not page or page[-1].sid == last_message.sid:
            break
        yield from page

print("Starting export process...")

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()

    # Fetch and write messages with progress bar
    with tqdm(desc="Exporting messages", unit="msg") as pbar:
        for message in fetch_messages(start_date, end_date):
            writer.writerow({
                'Date Sent': message.date_sent,
                'From': message.from_,
                'To': message.to,
                'Body': message.body
            })
            pbar.update(1)

print(f"Export complete. File saved as {csv_filename}")
print(f"Total messages exported: {pbar.n}")
