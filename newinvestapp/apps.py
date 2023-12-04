from django.apps import AppConfig


class NewinvestappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newinvestapp'

    def ready(self):
    	import newinvestapp.signals
