from django.apps import AppConfig

class ApiappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apiApp'

    def ready(self):
        # Import signals here — ensures apps are loaded first
        from . import signals
