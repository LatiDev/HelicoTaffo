import os, smtplib, pathlib
from email.message import EmailMessage

def base(from_: str, to: str, title: str, message: str) -> EmailMessage:
    email = EmailMessage()
    email["From"] = from_
    email["To"] = to
    email["Subject"] = title
    email.set_content(message)

    return email

def add_file(email: EmailMessage, file: str):
    path = pathlib.Path(file)
    email.add_attachment(
        path.read_bytes(), 
        maintype="application", 
        subtype=path.suffix, 
        filename=path.name
    )    

def add_files(email: EmailMessage, files: list = []):
    for file in files:
        add_file(email, file)

def send(email: EmailMessage, from_: str, password: str):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_, password)
        smtp.send_message(email)