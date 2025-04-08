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

