from django.contrib import admin
from .models import Creditos, Usuario, SaldoCredito,HistoricoConsumo

admin.site.register(Usuario)
admin.site.register(SaldoCredito)
admin.site.register(HistoricoConsumo)
admin.site.register(Creditos)