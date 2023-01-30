from gwpycore import mail_server, send_mail

RECIPIENT = "recipient@example.com"
EMAIL_SERVER = "imap.gmail.com"
EMAIL_PORT = 465
EMAIL_USERNAME = "sender@example.com"
EMAIL_PASSWORD = "its-a-secret"


def main():
    email_body = "This is a test email."
    attachments = ["C:\\out\\foo.txt"]

    with mail_server(
        server=EMAIL_SERVER,
        port=EMAIL_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD
    ) as smtp:
        send_mail(
            smtp,
            send_from=EMAIL_USERNAME,
            send_to=[RECIPIENT],
            subject="Test E-mail",
            body=email_body,
            attachments=attachments
        )


if __name__ == '__main__':
    main()
