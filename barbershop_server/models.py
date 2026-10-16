from django.db import models
from django.contrib.auth.models import User

# 💈 TABELA DE AGENDAMENTOS IMPERIAL COM TRACKING DE PAGAMENTO COMPLETO
class Agendamento(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    servico = models.CharField(max_length=100)
    barbeiro = models.CharField(max_length=100)
    data = models.CharField(max_length=20)
    horario = models.CharField(max_length=10)
    pago = models.BooleanField(default=False)
    valor_bruto = models.FloatField(default=85.00)
    desconto_aplicado = models.FloatField(default=0.00)
    # 🔑 A NOVA CHAVE DO CAIXA: Guarda se foi PIX, Cartão, Dinheiro ou Saldo!
    meio_pagamento = models.CharField(max_length=20, default='PIX')

    def __str__(self):
        return f"{self.cliente.username} - {self.servico} ({self.meio_pagamento})"

# 💰 TABELA DA CARTEIRA DIGITAL DE CASHBACK
class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    saldo_cashback = models.FloatField(default=15.00)

    def __str__(self):
        return f"Carteira de {self.user.username} - Saldo: R$ {self.saldo_cashback:.2f}"
