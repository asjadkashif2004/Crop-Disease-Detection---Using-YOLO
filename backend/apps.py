from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        # Pre-load the model when Django starts
        try:
            from .model_loader import get_model
            get_model()
        except Exception as e:
            print(f"[WARNING] Could not preload model on startup: {e}")
