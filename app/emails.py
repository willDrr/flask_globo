from flask_mail import Message
from app import mail, celery
from flask import render_template, url_for, current_app

@celery.task
def send_mail_with_celery(content):
    msg = create_message(content)
    mail.send(msg)

def send_mail(to, subjec, template, **kwargs):
    content = {
        "subject": subjec,
        "sender": "Globomantics Team <noreply@globomantics.com>",
        "recipients": [to],
        "template": template,
        "kwargs": kwargs
    }
    
    if current_app.config["SEND_MAILS_WITH_CELERY"]:
        send_mail_with_celery.delay(content) # send emails with celery
    else:
        msg = create_message(content)
        mail.send(msg)
    
def create_message(content):
    msg = Message(
        content["subject"],
        sender=content["sender"],
        recipients=content["recipients"]
    )
    msg.body = render_template(content["template"] + ".txt", **content["kwargs"])
    msg.html = render_template(content["template"] + ".html", **content["kwargs"])
    
    return msg

def send_activation_mail(user):
    send_mail(
        user.email,
        "Confirm your account",
        "emails/auth/confirm",
        username=user.username,
        role=user.role_id, 
        activation_link=url_for(
            "auth.activate_account",
            token=user.activation_token,
            _external=True
        )
    )
    
def send_password_reset_mail(user):
    send_mail(
        user.email, 
        "Reset password",
        "emails/auth/password_reset",
        username=user.username,
        role=user.role_id,
        password_reset_link=url_for(
            "auth.update_password",
            token=user.reset_token,
            email=user.email,
            _external=True
        )
    )    
    
    
    