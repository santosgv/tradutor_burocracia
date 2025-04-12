from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaldoCredito,Usuario

@receiver(post_save, sender=Usuario)
def update_user_credit(sender, instance, created, **kwargs):
    if created:
        SaldoCredito.objects.create(usuario=instance, creditos=5)