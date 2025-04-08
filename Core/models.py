from django.db import models
from Autenticacao.models import Usuario

class TermoJuridico(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='buscas')
    termo_buscado = models.TextField()  # Ex: "Aposentadoria por invalidez"
    traducao = models.TextField()                      # Ex: "Direito quando doença impede trabalho"
    lei_relacionada = models.CharField(max_length=100) # Ex: "Lei 8.213/91"
    tags = models.CharField(max_length=50)              # Ex: "INSS", "Direito Trabalhista"
    data_busca = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.email + " - " + self.tags

    class Meta:
        verbose_name = "Histórico de Busca"
        verbose_name_plural = "Históricos de Busca"
        ordering = ['-data_busca']