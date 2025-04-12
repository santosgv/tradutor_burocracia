# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    # Dados Básicos (obrigatórios para autenticação)
    email = models.EmailField(unique=True, verbose_name="E-mail")
    
    # Dados Demográficos (opcionais mas valiosos)
    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')],
        verbose_name="CPF"
    )
    data_nascimento = models.DateField(null=True, blank=True)
    telefone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\(\d{2}\) \d{4,5}-\d{4}$')]
    )
    
    # Dados Jurídicos Relevantes
    TEMAS_INTERESSE = [
        ('INSS', 'Previdência Social'),
        ('TRABALHISTA', 'Direito Trabalhista'),
        ('CONSUMIDOR', 'Direito do Consumidor'),
        ('FAMILIA', 'Direito de Família'),
    ]
    
    temas_interesse = models.JSONField(
        default=list,
        blank=True,
        help_text="Temas jurídicos de interesse do usuário"
    )
    
    # Consentimentos (essencial para LGPD)
    consentimento_contato_advogado = models.BooleanField(
        default=True,
        verbose_name="Autoriza contato por advogados parceiros?"
    )
    
    consentimento_analise_dados = models.BooleanField(
        default=True,
        verbose_name="Autoriza uso de dados para melhoria do serviço?"
    )
    
    # Metadados
    data_consentimento = models.DateTimeField(auto_now_add=True)
    ultima_busca = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última pesquisa realizada"
    )
    
    # Configurações
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        permissions = [
            ("pode_exportar_dados", "Pode exportar dados de usuários para parceiros"),
        ]
    
    def __str__(self):
        return self.email

class SaldoCredito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="saldo")
    creditos = models.IntegerField(default=0)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.email} - Créditos: {self.creditos}"

    def consumir_credito(self, quantidade=1):
        if self.creditos >= quantidade:
            self.creditos -= quantidade
            self.save()
            return True
        return False
    
class HistoricoConsumo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termo = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)
    creditos_usados = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.usuario.email} - {self.termo} - {self.data}"

class Creditos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    data_compra = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Créditos"

    def __str__(self):
        return f"{self.quantidade} créditos - {self.usuario.email}"