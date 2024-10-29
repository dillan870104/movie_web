from django.apps import AppConfig


class MovieTicketBookingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movie_ticket_booking"

    # def ready(self):
    #     from .scheduler import setup_scheduler

    #     setup_scheduler()
