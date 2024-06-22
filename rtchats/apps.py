from django.apps import AppConfig


class RtchatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rtchats'

    def ready(self):
        import rtchats.signals