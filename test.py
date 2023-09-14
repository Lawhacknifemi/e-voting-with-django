
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='goodness#gmail.com',
    to_emails='adediranao.18@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(api'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'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)

