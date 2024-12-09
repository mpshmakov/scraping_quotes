
import asyncio
import smtplib
from email.message import EmailMessage
from database.operations import generateAndUpdateConfirmCodeForUser
from secret import gmail_app_password, gmail_user, admin_emails as sent_to
import random

async def login_notifications(username: str):
    asyncio.gather(login_email_notification_admin(username), login_email_notification_user(username))
    print("admin, user login emails sent.")

async def register_notifications(username: str):
    asyncio.gather(registration_email_notification_admin(username), registration_email_notification_user(username))
    print("admin, user register emails sent.")

async def change_password_notifications(username: str):
    asyncio.gather(change_password_email_notification_admin(username), change_password_email_notification_user(username))
    print("admin, user change password emails sent.")


async def login_email_notification_admin(username: str):
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

async def registration_email_notification_admin(username: str):
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

async def registration_email_notification_user(username: str):
    sent_from = gmail_user
    sent_subject = "You have registered an account for quotes API."
    sent_body = (f"Thank you for the registration. Currenlty you don't have access to the data. Toggle your access with /user/toggle_access endpoint to get access.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = username

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def login_email_notification_user(username: str):
    sent_from = gmail_user
    sent_subject = "Someone has logged in to your account."
    sent_body = (f"This device <ip, device info and whatever> has logged into your account. Contact support if it wasn't you.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = username

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def change_password_email_notification_user(username: str):
    sent_from = gmail_user
    sent_subject = "Your password was changed."
    sent_body = (f"Your password was changed from this device: <device info>. Contact support if it wasn't you.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = username

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def change_password_email_notification_admin(username: str):
    sent_from = gmail_user
    sent_subject = f"{username} changed their password."
    sent_body = (f"{username} has changed their password from this device: <ip, device etc>.")

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

async def send_password_reset_code(email: str):
    code = generateAndUpdateConfirmCodeForUser(email)

    sent_from = gmail_user
    sent_subject = "Your password reset code."
    sent_body = (f"Your code for the resetting the password: {code}. Contact support you didn't request it.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def send_new_password(email: str, password: str):    
    sent_from = gmail_user
    sent_subject = "Your password reset code."
    sent_body = (f"Your new password: {password}. Contact support if you didn't request it.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def send_payment_succeeded_user(email: str, price:int, currency:str, item:str, receipt_url:str):    
    sent_from = gmail_user
    sent_subject = "Payment receipt."
    sent_body = (f"Your last payment of {price} {currency} for {item} was successful. Receipt url: {receipt_url}. Contact support for any questions.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)

async def send_payment_failed_user(email: str, price:int, currency:str, item:str):    
    sent_from = gmail_user
    sent_subject = "Payment receipt."
    sent_body = (f"Your last payment of {price} {currency} for {item} was unsuccessful. Contact support for any questions.")

    msg = EmailMessage()
    msg.set_content(sent_body)
    msg['Subject'] = sent_subject
    msg['From'] = sent_from
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.send_message(msg)    
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception) 