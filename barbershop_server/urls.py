from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from barbershop_server.models import Agendamento, PerfilCliente, CupomDesconto
from django.core.mail import send_mail
from datetime import datetime


class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'servico', 'barbeiro', 'data', 'horario', 'valor_bruto', 'desconto_aplicado',
                    'meio_pagamento', 'pago')
    list_filter = ('barbeiro', 'pago', 'meio_pagamento')
    search_fields = ('cliente__username', 'servico')


class PerfilClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'saldo_cashback')


class CupomDescontoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'valor_desconto', 'ativo')


if not admin.site.is_registered(Agendamento):
    admin.site.register(Agendamento, AgendamentoAdmin)

if not admin.site.is_registered(PerfilCliente):
    admin.site.register(PerfilCliente, PerfilClienteAdmin)

if not admin.site.is_registered(CupomDesconto):
    admin.site.register(CupomDesconto, CupomDescontoAdmin)


def pagina_inicial(request):
    return render(request, 'home.html')


def pagina_login(request):
    if request.method == 'POST':
        usuario_digitado = request.POST.get('username')
        senha_digitada = request.POST.get('password')
        usuario_validado = authenticate(request, username=usuario_digitado, password=senha_digitada)
        if usuario_validado is not None:
            auth_login(request, usuario_validado)
            user_instancia = User.objects.get(pk=usuario_validado.pk)
            PerfilCliente.objects.get_or_create(user=user_instancia)
            if user_instancia.username == 'maria':
                return redirect('central_financeira')
            if user_instancia.is_staff:
                return redirect('painel_barbeiro')
            return redirect('servicos')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha incorretos. Tente novamente, Soberana!'})
    return render(request, 'login.html')


def pagina_cadastro(request):
    if request.method == 'POST':
        usuario = request.POST.get('username').lower().strip()
        nome = request.POST.get('first_name')
        whats = request.POST.get('whatsapp')
        email_cliente = request.POST.get('email')
        senha_cliente = request.POST.get('password')
        if User.objects.filter(username=usuario).exists():
            return render(request, 'cadastro.html',
                          {'msg_alerta': 'Este nome de usuário já está sendo usado. Tente outro!'})
        novo_cliente = User.objects.create_user(username=usuario, email=email_cliente, password=senha_cliente,
                                                first_name=nome, last_name=whats)
        novo_cliente.save()
        PerfilCliente.objects.create(user=novo_cliente)
        return render(request, 'login.html', {'erro': 'Cadastro realizado com maestria! Faça o seu primeiro acesso.'})
    return render(request, 'cadastro.html')


def pagina_servicos(request):
    return render(request, 'servicos.html')


def pagina_agendamento(request):
    return render(request, 'agendamento.html')


def pagina_checkout(request):
    servico_real = request.POST.get('servico') or request.GET.get('servico', 'Combo Imperial Premium 👑')
    preco_real_str = request.POST.get('preco') or request.GET.get('preco', '85.00')
    try:
        preco_numero = float(preco_real_str)
    except ValueError:
        preco_numero = 85.00
    data_real = request.POST.get('data') or request.GET.get('data', '14/10/2026')
    horario_real = request.POST.get('horario') or request.GET.get('horario', '18:00h')

    saldo_atual = 15.00
    if request.user.is_authenticated:
        carteira, _ = PerfilCliente.objects.get_or_create(user=request.user)
        saldo_atual = carteira.saldo_cashback

    # 🔑 O MOTOR INTEGRAL DE VALIDAÇÃO DO CUPOM PROMOCIONAL:
    cupom_digitado = request.POST.get('cupom_promocional', '').upper().strip()
    desconto_cupom = 0.0
    msg_cupom_sucesso = ""
    msg_cupom_erro = ""

    if cupom_digitado:
        try:
            cupom_banco = CupomDesconto.objects.get(codigo=cupom_digitado, ativo=True)
            desconto_cupom = cupom_banco.valor_desconto
            msg_cupom_sucesso = f"✓ Cupom {cupom_digitado} aplicado! Desconto de R$ {desconto_cupom:.2f} garantido!"
        except CupomDesconto.DoesNotExist:
            msg_cupom_erro = "⚠️ Código promocional inválido ou já expirado!"

    # 📊 CÁLCULO FINAL DO NOVO CAIXA DO CLIENTE:
    preco_com_desconto_cupom = max(0.0, preco_numero - desconto_cupom)

    contexto = {
        'servico_escolhido': servico_real,
        'preco_escolhido': f"{preco_com_desconto_cupom:,.2f}".replace('.', ','),
        'preco_puro': preco_com_desconto_cupom,
        'preco_original': preco_numero,
        'data_escolhida': data_real,
        'horario_escolhido': horario_real,
        'saldo_real_banco': saldo_atual,
        'cupom_codigo': cupom_digitado,
        'desconto_cupom': desconto_cupom,
        'msg_cupom_sucesso': msg_cupom_sucesso,
        'msg_cupom_erro': msg_cupom_erro,
    }

    if request.method == 'POST' and 'finalizar_agendamento' in request.POST:
        if request.user.is_authenticated:
            usou_credito = request.POST.get('usou_cashback_flag') == 'sim'
            desconto_total_aplicado = desconto_cupom
            carteira = PerfilCliente.objects.get(user=request.user)

            if usou_credito:
                desconto_total_aplicado += carteira.saldo_cashback
                carteira.saldo_cashback = 0.0

            meio_escolhido = request.POST.get('meio_pagamento_ativo') or 'PIX'
            if usou_credito and preco_com_desconto_cupom <= desconto_total_aplicado:
                meio_escolhido = 'Saldo'

            novo_agendamento = Agendamento.objects.create(
                cliente=request.user,
                servico=servico_real,
                barbeiro="lucas.barber",
                data=data_real,
                horario=horario_real,
                pago=True,
                valor_bruto=preco_numero,
                desconto_applied=desconto_total_aplicado,
                meio_pagamento=meio_escolhido
            )
            novo_agendamento.save()

            bonus_novo = preco_com_desconto_cupom * 0.10
            carteira.saldo_cashback += bonus_novo
            carteira.save()

            email_do_cliente = request.user.email if request.user.email else "cliente@email.com"
            nome_do_cliente = request.user.first_name if request.user.first_name else request.user.username
            assunto = f"Confirmação Imperiosa - Seu lugar no trono está reservado! 🎉"
            corpo_mensagem = f"Olá, {nome_do_cliente}!\n\nSeu agendamento foi confirmado com cupom!\n\nAtenciosamente,\nBarberShop Imperial 👑"
            send_mail(assunto, corpo_mensagem, 'atendimento@barbershopimperial.com.br', [email_do_cliente],
                      fail_silently=True)
            return redirect('pagina_sucesso')

    return render(request, 'checkout.html', contexto)


def pagina_sucesso(request):
    return render(request, 'sucesso.html')


def pagina_barbeiro(request):
    if request.user.is_authenticated:
        user_instancia = User.objects.get(pk=request.user.pk)
        if user_instancia.username == 'maria':
            nome_barbeiro_logado = "Administradora Maria"
            cortes_filtrados = Agendamento.objects.all()
        else:
            nome_barbeiro_logado = user_instancia.first_name if user_instancia.first_name else user_instancia.username
            cortes_filtrados = Agendamento.objects.filter(barbeiro=user_instancia.username)
    else:
        nome_barbeiro_logado = "Visitante Imperial"
        cortes_filtrados = []
    contexto_barbeiro = {
        'barbeiro_nome': nome_barbeiro_logado,
        'lista_cortes': cortes_filtrados
    }
    return render(request, 'painel_barbeiro.html', contexto_barbeiro)


def central_financeira(request):
    todos_agendamentos = Agendamento.objects.all()
    total_cortes = todos_agendamentos.count()
    faturamento_bruto = sum(corte.valor_bruto for corte in todos_agendamentos)
    total_descontos = sum(corte.desconto_aplicado for corte in todos_agendamentos)
    lucro_liquido = faturamento_bruto - total_descontos
    ticket_calculado = 85.00 if total_cortes == 0 else lucro_liquido / total_cortes
    total_pix = sum((c.valor_bruto - c.desconto_aplicado) for c in todos_agendamentos if c.meio_pagamento == 'PIX')
    total_cartao = sum(
        (c.valor_bruto - c.desconto_aplicado) for c in todos_agendamentos if c.meio_pagamento in ['Cartão', 'Cartao'])
    total_especie = sum((c.valor_bruto - c.desconto_aplicado) for c in todos_agendamentos if
                        c.meio_pagamento in ['Dinheiro', 'Espécie', 'Especie'])
    total_saldo = sum((c.valor_bruto - c.desconto_aplicado) for c in todos_agendamentos if c.meio_pagamento == 'Saldo')

    contagem_dias = {"Seg": 0, "Ter": 0, "Qua": 0, "Qui": 0, "Sex": 0, "Sáb": 0, "Dom": 0}
    mapa_dias = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}

    for corte in todos_agendamentos:
        data_objeto = None
        for formato in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]:
            try:
                data_objeto = datetime.strptime(corte.data.strip(), formato)
                break
            except ValueError:
                pass
        if data_objeto:
            numero_dia = data_objeto.weekday()
            sigla_dia = mapa_dias[numero_dia]
            contagem_dias[sigla_dia] += 1

    # 📊 CÁLCULO INVISÍVEL DAS PORCENTAGENS DIRETO NO PYTHON:
    maior_volume = max(contagem_dias.values()) if max(contagem_dias.values()) > 0 else 1
    larguras = {dia: (qtd / maior_volume) * 100 for dia, qtd in contagem_dias.items()}

    # 🎟️ VARREDURA IMPERIAL RECALIBRADA:
    cupons_utilizados = []
    for corte in todos_agendamentos:
        if corte.desconto_aplicado > 0:
            cupons_utilizados.append({
                'cliente': corte.cliente.first_name if corte.cliente.first_name else corte.cliente.username,
                'servico': corte.servico,
                'data': corte.data,
                'desconto': f"{corte.desconto_aplicado:,.2f}".replace('.', ',')
            })


    contexto_financeiro = {
        'total_faturado': f"{faturamento_bruto:,.2f}".replace('.', ','),
        'total_descontos': f"{total_descontos:,.2f}".replace('.', ','),
        'lucro_liquido': f"{lucro_liquido:,.2f}".replace('.', ','),
        'total_cortes': total_cortes,
        'ticket_medio': f"{ticket_calculado:,.2f}".replace('.', ','),
        'total_pix': f"{total_pix:,.2f}".replace('.', ','),
        'total_cartao': f"{total_cartao:,.2f}".replace('.', ','),
        'total_especie': f"{total_especie:,.2f}".replace('.', ','),
        'total_saldo': f"{total_saldo:,.2f}".replace('.', ','),
        'seg': contagem_dias["Seg"], 'ter': contagem_dias["Ter"], 'qua': contagem_dias["Qua"],
        'qui': contagem_dias["Qui"], 'sex': contagem_dias["Sex"], 'sáb': contagem_dias["Sáb"],
        'dom': contagem_dias["Dom"],
        'w_seg': larguras["Seg"], 'w_ter': larguras["Ter"], 'w_qua': larguras["Qua"],
        'w_qui': larguras["Qui"], 'w_sex': larguras["Sex"], 'w_sab': larguras["Sáb"],
        'w_dom': larguras["Dom"],
        # 🔑 A CHAVE DA AUDITORIA ENVIADA PARA A TELA:
        'cupons_utilizados': cupons_utilizados
    }
    return render(request, 'faturamento.html', contexto_financeiro)


def cadastrar_barbeiro(request):
    contexto = {'msg_alerta': '', 'msg_sucesso': ''}
    if request.method == 'POST':
        usuario = request.POST.get('username', '').lower().strip()
        nome_completo = request.POST.get('first_name', '')
        senha = request.POST.get('password', '')
        if User.objects.filter(username=usuario).exists():
            contexto['msg_alerta'] = 'Este login já pertence a um profissional da rede!'
        else:
            novo_barbeiro = User.objects.create_user(username=usuario, password=senha, first_name=nome_completo)
            novo_barbeiro.is_staff = True
            novo_barbeiro.save()
            PerfilCliente.objects.create(user=novo_barbeiro)
            contexto['msg_sucesso'] = f'✓ Profissional {nome_completo} credenciado com sucesso no sistema!'
    return render(request, 'cadastro_barbeiro.html', contexto)

def cadastrar_cupom(request):
    contexto = {
        'msg_alerta': '',
        'msg_sucesso': '',
        'lista_cupons': CupomDesconto.objects.all().order_by('-id')
    }
    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo', '').upper().strip()
        valor_digitado_str = request.POST.get('valor_desconto', '0')
        try:
            valor_numero = float(valor_digitado_str)
            if CupomDesconto.objects.filter(codigo=codigo_digitado).exists():
                contexto['msg_alerta'] = 'Este código promocional já está ativo no sistema!'
            else:
                CupomDesconto.objects.create(codigo=codigo_digitado, valor_desconto=valor_numero, ativo=True)
                contexto['msg_sucesso'] = f'✓ Cupom {codigo_digitado} com desconto de R$ {valor_numero:.2f} ativado com maestria!'
                contexto['lista_cupons'] = CupomDesconto.objects.all().order_by('-id')
        except ValueError:
            contexto['msg_alerta'] = 'Formato de valor incorreto. Use números válidos!'
    return render(request, 'cadastro_cupom.html', contexto)

def disparar_whatsapp(_request, corte_id):
    corte = get_object_or_404(Agendamento, pk=corte_id)
    telefone_limpo = "".join(c for c in corte.cliente.last_name if c.isdigit())
    if not telefone_limpo.startswith("55") and len(telefone_limpo) >= 10:
        telefone_limpo = "55" + telefone_limpo
    nome_cliente = corte.cliente.first_name if corte.cliente.first_name else corte.cliente.username
    mensagem_texto = f"Olá, {nome_cliente}! 👑\n\nLembrete de agendamento de {corte.servico} para o dia {corte.data} às {corte.horario}! 🪒"
    texto_codificado = mensagem_texto.replace('\n', '%0A').replace(' ', '%20').replace('!', '%21')
    return redirect(f"https://wa.me{telefone_limpo}?text={texto_codificado}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pagina_inicial, name='home'),
    path('login/', pagina_login, name='login'),
    path('cadastro/', pagina_cadastro, name='cadastro'),
    path('servicos/', pagina_servicos, name='servicos'),
    path('agendamento/', pagina_agendamento, name='agendamento'),
    path('checkout/', pagina_checkout, name='checkout'),
    path('painel-barbeiro/', pagina_barbeiro, name='painel_barbeiro'),
    path('reserva-confirmada/', pagina_sucesso, name='pagina_sucesso'),
    path('central-lucros/', central_financeira, name='central_financeira'),
    path('cadastrar-barbeiro/', cadastrar_barbeiro, name='cadastrar_barbeiro'),
    path('fabrica-cupons/', cadastrar_cupom, name='cadastrar_cupom'),
    path('disparar-zap/<int:corte_id>/', disparar_whatsapp, name='enviar_lembrete'),
]
