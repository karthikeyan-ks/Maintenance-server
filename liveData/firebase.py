import os
import firebase_admin
from firebase_admin import credentials, messaging

from WebMaintain.settings import BASE_DIR
import json

# Path to the service account key file
SERVICE_ACCOUNT_KEY_FILE = os.path.join(BASE_DIR, "liveData", "google-services.json")

# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_FILE)
firebase_admin.initialize_app(cred)


def send_notification(token, title, body):
    message = messaging.Message(
        data={
            'broadcast': str(False),
            'title': title,
            'body': body
        },
        token=token,
    )
    response = messaging.send(message)
    print("Successfully sent message:", response)


def sendBroadCast(subscription, data):
    message = messaging.Message(
        data=data,
        topic=subscription
    )
    messaging.send(message)
