from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    """
    Configuration for the News application.
    This class sets the default auto field type and imports signals when the app is ready.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_app"

    def ready(self):
        # Import signals here so they are registered when Django starts
        import news_app.signals
