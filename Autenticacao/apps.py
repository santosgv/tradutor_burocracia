from django.apps import AppConfig


class AutenticacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Autenticacao'

    def ready(self):
        import Autenticacao.signals 

