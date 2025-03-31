from . import SecureNotificationService
from database.models import User


class EmailNotificationService(SecureNotificationService):
    def __init__(self, user: User):
        self.email = user.email
        assert self.email is not None, "User email is None"

    def send_notification(self, subject: str, message: str) -> None:
        # Here you would implement the actual email sending logic.
        # For demonstration purposes, we'll just print the email.
        print(f"Sending email to {self.email} with subject '{subject}' and message '{message}'")
