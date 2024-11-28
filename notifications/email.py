
import smtplib
from email.message import EmailMessage
from secret import gmail_app_password, gmail_user, admin_emails as sent_to

def login_email_notification(username: str):
    sent_from = gmail_user
    sent_subject = "User logon to quotes api"
    sent_body = (f"{username} has logged on to the system.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = ', '.join(sent_to)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

def registration_email_notification(username: str):
    sent_from = gmail_user
    sent_subject = "User registered to quotes api"
    sent_body = (f"{username} has registered to the system.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = ', '.join(sent_to)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)