from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync
from src.config import Config

if Config.ENABLE_CELERY and Config.REDIS_URL:
    c_app = Celery("bookly_backend", broker=Config.REDIS_URL, backend=Config.REDIS_URL)
    c_app.conf.update(broker_connection_retry_on_startup=True)
else:
    c_app = Celery("bookly_backend", broker="memory://", backend="cache+memory://")
    c_app.conf.update(task_always_eager=True)

c_app.config_from_object('src.config')

@c_app.task()

def send_email(recipients: list[str],subject: str, body: str):
    message = create_message(
    recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)



