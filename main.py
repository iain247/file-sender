from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

WATCH_FOLDER = "/watch"
SENT_FILES_NAME = "/config/sent_files.txt"

class FileHandler(FileSystemEventHandler):
    def __init__(self, sender_host, sender_email, sender_password, destination_email):
        self.sender_host = sender_host
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.destination_email = destination_email

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}", flush=True)
            # TODO: Check if the file has already been sent? Use a text file to track sent files?
            if event.src_path in read_sent_files():
                print("File has already been sent to kindle", flush=True)
            else:
                send_email(event.src_path, self.sender_host, self.sender_email, self.sender_password, self.destination_email)
                add_sent_file(event.src_path)

def send_email(file_path, sender_host, sender_email, sender_password, destination_email):
    subject = "New file!"

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = destination_email
    msg["Subject"] = subject
    msg.set_content(f"Sending new file: {os.path.basename(file_path)}")

    with open(file_path, "rb") as file:
        msg.add_attachment(file.read(), maintype="application", subtype="octet-stream",
                           filename=os.path.basename(file_path))

    with smtplib.SMTP(sender_host, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Email sent to {destination_email}", flush=True)

def read_sent_files():
    with open(SENT_FILES_NAME, "r") as file:
        return [line.strip() for line in file]

def add_sent_file(filename):
    with open(SENT_FILES_NAME, "a") as file:
        file.write(filename + "\n")

def main():
    load_dotenv()
    sender_host = os.getenv("SENDER_SMTP_HOST")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    destination_email = os.getenv("DESTINATION_EMAIL")

    event_handler = FileHandler(sender_host, sender_email, sender_password, destination_email)
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
