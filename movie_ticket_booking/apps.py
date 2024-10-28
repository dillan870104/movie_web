from django.apps import AppConfig
import threading
from django.utils import timezone


class MovieTicketBookingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movie_ticket_booking"

    def ready(self):
        thread = threading.Thread(target=self.run_task)

    def run_task(self):
        print("排成以執行", timezone.now())
