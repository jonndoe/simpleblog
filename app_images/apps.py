from django.apps import AppConfig


class AppImagesConfig(AppConfig):
    name = 'app_images'

    def ready(self):
        # import signal handlers
        import app_images.signals
