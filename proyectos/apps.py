from django.apps import AppConfig


class ProyectosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectos'

    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Importa los signals para que se registren automáticamente.
        """
        import proyectos.signals
