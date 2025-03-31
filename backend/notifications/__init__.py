from abc import ABC, abstractmethod


class NotificationServiceInterface(ABC):
    @abstractmethod
    def send_notification(self, subject: str, message: str) -> None:
        """Send a notification with the given message."""
        pass

class SecureNotificationService(NotificationServiceInterface):
    @abstractmethod
    def send_notification(self, subject: str, message: str) -> None:
        """Send a secure notification with the given message."""
        pass
