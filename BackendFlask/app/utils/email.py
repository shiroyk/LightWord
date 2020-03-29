import random, threading

from flask import copy_current_request_context, current_app
from flask_mail import Message
from app import mail

def generate_code(code = []):
    for i in range(1,10):
        num = random.randint(0, 9)
        upper = chr(random.randint(65, 90))
        lower = chr(random.randint(97, 122))
        code.append(str(num))
        code.append(upper)
        code.append(lower)
    return ''.join(code)[num:num+6]

def send_email(subject, sender, recipients, msg_body, msg_html,
               **kwargs):
    message = Message(subject,
                      sender=sender,
                      recipients=recipients,
                      **kwargs)
    message.body = msg_body
    message.html = msg_html

    @copy_current_request_context
    def send_message(message,):
        try:
            mail.send(message)
        except Exception as e:
            current_app.logger.error('%s: Send email failed, please check config', __name__)
    
    sender = threading.Thread(target=send_message, args=(message,))
    sender.start()
    return sender
