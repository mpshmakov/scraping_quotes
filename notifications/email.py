
import smtplib
from secret import gmail_app_password, gmail_user

def login_email_notification(username: str):
    # print("notification")
    sent_from = gmail_user
    sent_to = ['shmakov.mp@gmail.com', 'zeras4z4@gmail.com']
    sent_subject = "User logon to quotes api"
    sent_body = (f"{username} has logged on to the system.")

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    print(email_text)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)