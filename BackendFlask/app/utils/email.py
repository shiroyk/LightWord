import random, threading

from flask import copy_current_request_context
from flask_mail import Message
from app import mail

def generate_code(code = []):
    random_num = random.randint(0, 9)
    random_upper = chr(random.randint(65, 90))
    random_lower = chr(random.randint(97, 122))
    code.append(str(random_num))
    code.append(random_upper)
    code.append(random_lower)
    if len(code) != 6:
        generate_code(code)
        return ''.join(code)

def send_email(subject, sender, recipients, msg_body, msg_html,
               **kwargs):

    message = Message(subject,
                      sender=sender,
                      recipients=recipients,
                      **kwargs)
    message.body = msg_body
    message.html = msg_html
    @copy_current_request_context
    def send_message(message):
        mail.send(message)

    sender = threading.Thread(target=send_message, args=(message,))
    sender.start()
    return sender
