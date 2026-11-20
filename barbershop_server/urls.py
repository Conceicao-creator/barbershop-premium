# suppress PyUnresolvedReferences, PyShadowingNames, PyUnusedLocal
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth import authenticate, login as auth_login
import csv
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from .models import Agendamento, CupomDesconto, VisitaApp
from .models import Agendamento, CupomDesconto, VisitaApp, ServicoBarbearia
from django.urls import path, reverse






# CODIGO DE SEGURANCA PARA IMPORTACAO DOS MODELOS DO BANCO:
from barbershop_server.models import Agendamento, PerfilCliente, CupomDesconto


# ROTAS INICIAIS E SIMULACOES DE PAGINAS:
def registrar_visita(request):
    if not request.session.get('visita_registrada'):
        agente = request.META.get('HTTP_USER_AGENT', '').lower()
        tipo_aparelho = 'Celular' if ('mobile' in agente or 'android' in agente or 'iphone' in agente) else 'Computador'
        VisitaApp.objects.create(dispositivo=tipo_aparelho)
        request.session['visita_registrada'] = True


def pagina_inicial(request):
    registrar_visita(request)
    return render(request, 'home.html')


def pagina_login(request):
    registrar_visita(request)
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
            return render(request, 'login.html', {'erro': 'Usuário ou senha incorretos. Tente novamente!'})
    return render(request, 'login.html')


def pagina_cadastro(request):
    contexto = {'msg_sucesso': '', 'msg_erro': '', 'usuario_criado': ''}
    if request.method == 'POST':
        usuario = request.POST.get('username', '').lower().strip().replace(' ', '.')
        nome = request.POST.get('first_name', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('password', '')

        if User.objects.filter(username=usuario).exists():
            contexto['msg_erro'] = '⚠️ Este login já está em uso. Escolha outro!'
        else:
            novo_cliente = User.objects.create_user(
                username=usuario,
                first_name=nome,
                last_name=whatsapp,
                email=email,
                password=senha
            )
            novo_cliente.save()
            PerfilCliente.objects.get_or_create(user=novo_cliente)
            contexto['usuario_criado'] = usuario
            contexto['msg_sucesso'] = f'✓ Cadastro realizado com sucesso, {nome}! Seu login é: {usuario}'
    return render(request, 'cadastro.html', contexto)


def pagina_redefinir_senha(request):
    contexto = {'msg_erro': '', 'msg_sucesso': '', 'usuario_confirmado': ''}
    if request.method == 'POST':
        usuario = request.POST.get('username', '').lower().strip()
        whatsapp_digitado = ''.join(filter(str.isdigit, request.POST.get('whatsapp', '')))
        nova_senha = request.POST.get('nova_senha', '').strip()

        user_encontrado = User.objects.filter(username=usuario).first()
        if not user_encontrado:
            contexto['msg_erro'] = '⚠️ Usuário não encontrado! Verifique seu login.'
        else:
            whatsapp_banco = ''.join(filter(str.isdigit, user_encontrado.last_name or ''))
            if whatsapp_digitado and whatsapp_digitado == whatsapp_banco:
                user_encontrado.set_password(nova_senha)
                user_encontrado.save()
                contexto['usuario_confirmado'] = usuario
                contexto['msg_sucesso'] = f'✓ Senha atualizada com sucesso para {usuario}!'
            else:
                contexto['msg_erro'] = '⚠️ O WhatsApp informado não confere com o cadastro deste usuário.'
    return render(request, 'redefinir_senha.html', contexto)




def pagina_servicos(request):
    registrar_visita(request)

def pagina_servicos(request):
    def registrar_visita(request):
        if not request.session.get('visita_registrada'):
            agente = request.META.get('HTTP_USER_AGENT', '').lower()
            tipo_aparelho = 'Celular' if (
                        'mobile' in agente or 'android' in agente or 'iphone' in agente) else 'Computador'
            VisitaApp.objects.create(dispositivo=tipo_aparelho)
            request.session['visita_registrada'] = True

    meus_cortes = []
    saldo_cliente = "0,00"
    if request.user.is_authenticated:
        meus_cortes = Agendamento.objects.filter(cliente=request.user).order_by('-id')
        from datetime import datetime
        hoje = datetime.now().date()
        for corte in meus_cortes:
            corte.valor_final = max(0.0, corte.valor_bruto - corte.desconto_aplicado)
            try:
                data_corte = datetime.strptime(corte.data.strip(), '%d/%m/%Y').date()
                corte.expirado = data_corte < hoje
            except ValueError:
                corte.expirado = False

        carteira, _ = PerfilCliente.objects.get_or_create(user=request.user)
        saldo_cliente = f"{carteira.saldo_cashback:,.2f}".replace('.', ',')
    return render(request, 'servicos.html', {
        'meus_cortes': meus_cortes,
        'saldo_cliente': saldo_cliente,
        'servicos_extras': ServicoBarbearia.objects.filter(ativo=True),
    })

def pagina_agendamento(request):
    return render(request, 'agendamento.html')


def pagina_barbeiro(request):
    if request.user.is_authenticated and request.user.is_staff and request.user.username != 'maria':
        agendamentos_painel = Agendamento.objects.filter(barbeiro=request.user.username).order_by('-id')
    else:
        agendamentos_painel = Agendamento.objects.all().order_by('-id')
    return render(request, 'painel_barbeiro.html', {
        'lista_cortes': agendamentos_painel,
    })



def pagina_sucesso(request):
        return render(request, 'sucesso.html')


# INTEGRACAO REAL DO CUPOM NO CHECKOUT COM ESCOLHA DE BARBEIRO:
def pagina_checkout(request):
        servico_real = request.POST.get('servico') or request.GET.get('servico', 'Combo Imperial Premium')
        preco_real_str = request.POST.get('preco') or request.GET.get('preco', '85.00')
        try:
            preco_numero = float(str(preco_real_str).replace(',', '.'))
        except Exception:
            preco_numero = 85.00

        data_real = request.POST.get('data') or request.GET.get('data', '14/10/2026')
        horario_real = request.POST.get('horario') or request.GET.get('horario', '18:00h')

        saldo_atual = 15.00
        if request.user.is_authenticated:
            carteira, _ = PerfilCliente.objects.get_or_create(user=request.user)
            saldo_atual = carteira.saldo_cashback

        cupom_digitado = request.POST.get('cupom_promocional', '').upper().strip()
        desconto_cupom = 0.0
        msg_cupom_sucesso = ""
        msg_cupom_erro = ""

        if cupom_digitado:
            try:
                cupom_banco = CupomDesconto.objects.get(codigo=cupom_digitado, ativo=True)
                desconto_cupom = cupom_banco.valor_desconto
                msg_cupom_sucesso = f"Cupom {cupom_digitado} aplicado!"
            except CupomDesconto.DoesNotExist:
                msg_cupom_erro = "⚠️ Código promocional inválido!"

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
            'lista_barbeiros': User.objects.filter(is_staff=True).exclude(username='maria'),
        }

        if request.method == 'POST' and 'finalizar_agendamento' in request.POST:
            if request.user.is_authenticated:
                meio_escolhido = request.POST.get('meio_pagamento_ativo') or 'PIX'
                usou_credito = (request.POST.get('usou_cashback_flag') == 'sim') or (meio_escolhido == 'Saldo')
                desconto_total_aplicado = desconto_cupom
                carteira = PerfilCliente.objects.get(user=request.user)


                if usou_credito:
                    abatimento_saldo = min(preco_com_desconto_cupom, carteira.saldo_cashback)
                    desconto_total_aplicado += abatimento_saldo
                    carteira.saldo_cashback = round(carteira.saldo_cashback - abatimento_saldo, 2)


                meio_escolhido = request.POST.get('meio_pagamento_ativo') or 'PIX'
                if usou_credito and preco_com_desconto_cupom <= desconto_total_aplicado:
                    meio_escolhido = 'Saldo'

                barbeiro_escolhido = request.POST.get('barbeiro_escolhido') or 'lucas.barber'
                horario_ocupado = Agendamento.objects.filter(
                    barbeiro=barbeiro_escolhido,
                    data=data_real,
                    horario=horario_real
                ).exists()

                if horario_ocupado:
                    contexto[
                        'msg_cupom_erro'] = f"⚠️ O profissional {barbeiro_escolhido} já possui um corte agendado em {data_real} às {horario_real}. Escolha outro barbeiro ou horário!"
                    return render(request, 'checkout.html', contexto)

                ja_existe = Agendamento.objects.filter(
                    data=data_real.strip(), horario=horario_real.strip(), cliente=request.user
                ) | Agendamento.objects.filter(
                    data=data_real.strip(), horario=horario_real.strip(), barbeiro=barbeiro_escolhido
                )

                if ja_existe.exists():
                    contexto['msg_cupom_erro'] = f'⚠️ Horário indisponível! Já existe agendamento para {data_real} às {horario_real}.'
                    return render(request, 'checkout.html', contexto)


                ja_esta_pago = meio_escolhido in ['PIX', 'Saldo']

                novo_agendamento = Agendamento.objects.create(
                    cliente=request.user,
                    servico=servico_real,
                    barbeiro=barbeiro_escolhido,
                    data=data_real,
                    horario=horario_real,
                    pago=ja_esta_pago,
                    valor_bruto=preco_numero,
                    desconto_aplicado=desconto_total_aplicado,
                    meio_pagamento=meio_escolhido
                )
                novo_agendamento.save()


                bonus_novo = preco_com_desconto_cupom * 0.00
                carteira.saldo_cashback += bonus_novo
                carteira.save()

                return redirect('pagina_sucesso')

        return render(request, 'checkout.html', contexto)


# CENTRAL FINANCEIRA COM FILTRO DE BARBEIROS E AUDITORIA FISCAL DINAMICA:
def central_financeira(request):
    barbeiro_selecionado = request.GET.get('barbeiro_filtro', 'todos')

    if barbeiro_selecionado == 'todos':
        todos_agendamentos = Agendamento.objects.all()
    else:
        todos_agendamentos = Agendamento.objects.filter(barbeiro=barbeiro_selecionado)

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

    maior_volume = max(contagem_dias.values()) if max(contagem_dias.values()) > 0 else 1
    larguras = {dia: (qtd / maior_volume) * 100 for dia, qtd in contagem_dias.items()}

    cupons_utilizados = []
    for corte in todos_agendamentos:
        if corte.desconto_aplicado > 0:
            liquido_corte = max(0.0, corte.valor_bruto - corte.desconto_aplicado)
            cupons_utilizados.append({
                'cliente': corte.cliente.first_name if corte.cliente.first_name else corte.cliente.username,
                'servico': corte.servico,
                'data': corte.data,
                'valor_bruto': f"{corte.valor_bruto:,.2f}".replace('.', ','),
                'desconto': f"{corte.desconto_aplicado:,.2f}".replace('.', ','),
                'valor_liquido': f"{liquido_corte:,.2f}".replace('.', ','),
                'meio_pagamento': corte.meio_pagamento or 'PIX',
            })

    meta_mensal = 2500.00
    porcentagem_meta = min(100, int((lucro_liquido / meta_mensal) * 100)) if meta_mensal > 0 else 0
    falta_meta = max(0.0, meta_mensal - lucro_liquido)
    avaliacoes_validas = [c.avaliacao for c in todos_agendamentos if c.avaliacao > 0]
    total_avaliacoes = len(avaliacoes_validas)
    media_avaliacao = f"{(sum(avaliacoes_validas) / total_avaliacoes):.1f}".replace('.', ',') if total_avaliacoes > 0 else "5,0"

    total_visitas = VisitaApp.objects.count()
    visitas_hoje = VisitaApp.objects.filter(data_hora__date=timezone.now().date()).count()
    visitas_celular = VisitaApp.objects.filter(dispositivo='Celular').count()
    visitas_pc = VisitaApp.objects.filter(dispositivo='Computador').count()
    pct_celular = int((visitas_celular / total_visitas) * 100) if total_visitas > 0 else 0

    usuarios_clientes = User.objects.filter(is_staff=False, is_superuser=False).order_by('id')
    lista_clientes_cadastrados = []
    for indice, cli in enumerate(usuarios_clientes, start=1):
        carteira_cli, _ = PerfilCliente.objects.get_or_create(user=cli)
        lista_clientes_cadastrados.append({
            'numero': indice,
            'nome': cli.first_name if cli.first_name else cli.username,
            'usuario': cli.username,
            'whatsapp': cli.last_name if cli.last_name else 'Não informado',
            'email': cli.email if cli.email else '-',
            'cashback': f"{carteira_cli.saldo_cashback:,.2f}".replace('.', ','),
            'data_cadastro': cli.date_joined.strftime('%d/%m/%Y') if cli.date_joined else '-',
        })



    contexto_financeiro = {
        'barbeiro_atual': barbeiro_selecionado,
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
        'cupons_utilizados': cupons_utilizados,
        'lista_barbeiros_banco': User.objects.filter(is_staff=True),
        'meta_mensal': f"{meta_mensal:,.2f}".replace('.', ','),
        'porcentagem_meta': porcentagem_meta,
        'falta_meta': f"{falta_meta:,.2f}".replace('.', ','),
        'media_avaliacao': media_avaliacao,
        'total_avaliacoes': total_avaliacoes,
        'total_visitas': total_visitas,
        'visitas_hoje': visitas_hoje,
        'visitas_celular': visitas_celular,
        'visitas_pc': visitas_pc,
        'pct_celular': pct_celular,
        'lista_clientes_cadastrados': lista_clientes_cadastrados,
        'total_clientes': len(lista_clientes_cadastrados),

    }
    return render(request, 'faturamento.html', contexto_financeiro)


# CADASTRO DE BARBEIRO COM IS_STAFF AUTOMATICO:
def cadastrar_barbeiro(request):
    msg_sucesso = ""
    msg_erro = ""
    if request.method == 'POST':
        usuario = request.POST.get('username', '').lower().strip().replace(' ', '.')
        nome = request.POST.get('first_name', '').strip()
        senha = request.POST.get('password', '')

        if not usuario:
            contexto['msg_erro'] = '⚠️ Digite um nome de usuário válido!'
        elif User.objects.filter(username=usuario).exists():
            contexto['msg_erro'] = f"⚠️ O login '{usuario}' já está em uso. Escolha outro!"

        else:
            novo_barbeiro = User.objects.create_user(
                username=usuario,
                first_name=nome,
                password=senha,
                is_staff=True
            )
            novo_barbeiro.save()
            msg_sucesso = f"✓ Profissional {nome} ({usuario}) credenciado com sucesso!"
    return render(request, 'cadastro_barbeiro.html', {'msg_sucesso': msg_sucesso, 'msg_erro': msg_erro})


# FABRICA DE CUPONS PROMOCIONAIS:
from urllib.parse import quote


def cadastrar_cupom(request):
    msg_sucesso = ""
    msg_erro = ""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').upper().strip()
        valor = request.POST.get('valor_desconto', '0.00')
        try:
            valor_num = float(valor)
            if CupomDesconto.objects.filter(codigo=codigo).exists():
                msg_erro = f"O cupom {codigo} já está cadastrado na fábrica!"
            else:
                CupomDesconto.objects.create(codigo=codigo, valor_desconto=valor_num, ativo=True)
                msg_sucesso = f"✓ Cupom {codigo} de R$ {valor_num:.2f} fabricado com sucesso!"
        except ValueError:
            msg_erro = "Digite um valor de desconto numérico válido!"

        lista_cupons = CupomDesconto.objects.filter(ativo=True).exclude(codigo='').order_by('-id')

        return render(request, 'cadastro_cupom.html', {'msg_sucesso': msg_sucesso, 'msg_erro': msg_erro, 'lista_cupons': lista_cupons})



def disparar_zap(request, agendamento_id):
    from urllib.parse import quote

    corte = Agendamento.objects.filter(id=agendamento_id).first()
    if not corte:
        return redirect('painel_barbeiro')

    nome_cliente = corte.cliente.first_name or corte.cliente.username
    telefone_bruto = ''.join(filter(str.isdigit, corte.cliente.last_name or ''))
    if telefone_bruto and not telefone_bruto.startswith('55'):
        telefone_bruto = '55' + telefone_bruto

    mensagem = (
        f"Olá, {nome_cliente}! 👑\n\n"
        f"Passando para lembrar do seu agendamento na *BarberShop Premium*:\n"
        f"✂️ *Serviço:* {corte.servico}\n"
        f"📅 *Data:* {corte.data} às {corte.horario}\n\n"
        f"Te aguardamos no trono!"
    )
    texto_codificado = quote(mensagem, encoding='utf-8')
    if telefone_bruto:
        url_zap = f"https://wa.me/{telefone_bruto}?text={texto_codificado}"
    else:
        url_zap = f"https://wa.me/?text={texto_codificado}"

    return redirect(url_zap)


def cancelar_corte(request, agendamento_id):
    if request.user.is_authenticated:
        corte = Agendamento.objects.filter(id=agendamento_id, cliente=request.user).first()
        if corte:
            corte.delete()
    return redirect('servicos')

def confirmar_pagamento(request, agendamento_id):
    if request.user.is_authenticated and request.user.is_staff:
        corte = Agendamento.objects.filter(id=agendamento_id).first()
        if corte:
            corte.pago = True
            corte.meio_pagamento = f"{corte.meio_pagamento} (Pago)"
            corte.save()
    return redirect('painel_barbeiro')



def exportar_caixa(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="relatorio_caixa_barbershop.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Data', 'Horario', 'Cliente', 'Barbeiro', 'Servico', 'Pagamento', 'Valor Bruto (R$)', 'Desconto (R$)', 'Lucro Liquido (R$)'])

    for corte in Agendamento.objects.all().order_by('-id'):
        nome_cliente = corte.cliente.first_name or corte.cliente.username
        liquido = corte.valor_bruto - corte.desconto_aplicado
        writer.writerow([
            corte.id,
            corte.data,
            corte.horario,
            nome_cliente,
            corte.barbeiro,
            corte.servico,
            corte.meio_pagamento,
            f"{corte.valor_bruto:.2f}".replace('.', ','),
            f"{corte.desconto_aplicado:.2f}".replace('.', ','),
            f"{liquido:.2f}".replace('.', ',')
        ])

    return response

def avaliar_corte(request, agendamento_id, nota):
    if request.user.is_authenticated and 1 <= nota <= 5:
        corte = Agendamento.objects.filter(id=agendamento_id, cliente=request.user).first()
        if corte:
            corte.avaliacao = nota
            corte.save()
    return redirect(f"{reverse('servicos')}#historico")

def manifesto_pwa(request):
    return render(request, 'manifest.json', content_type='application/json')

def service_worker_pwa(request):
    return render(request, 'sw.js', content_type='application/javascript')
def icone_app_pwa(request):
    caminho_icone = settings.BASE_DIR / 'templates' / 'icone_app.png'
    with open(caminho_icone, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/png')

def gerenciar_servicos(request):
    if not request.user.is_authenticated or request.user.username != 'maria':
        return redirect('login')
    msg_sucesso = ''
    if request.method == 'POST':
        if request.POST.get('remover_id'):
            ServicoBarbearia.objects.filter(id=request.POST.get('remover_id')).delete()
            msg_sucesso = '✓ Serviço removido do catálogo!'
        elif request.POST.get('criar_servico'):
            ServicoBarbearia.objects.create(
                nome=request.POST.get('nome', '').strip(),
                descricao=request.POST.get('descricao', '').strip() or 'Atendimento premium BarberShop.',
                preco=float(request.POST.get('preco', 50)),
                icone=request.POST.get('icone', '✂️')
            )
            msg_sucesso = '✓ Novo serviço adicionado com sucesso!'
    servicos = ServicoBarbearia.objects.all().order_by('-id')
    return render(request, 'gerenciar_servicos.html', {'servicos': servicos, 'msg_sucesso': msg_sucesso})

    def pagina_redefinir_senha(request):
        contexto = {'msg_erro': '', 'msg_sucesso': '', 'usuario_confirmado': ''}
        if request.method == 'POST':
            usuario = request.POST.get('username', '').lower().strip()
            whatsapp_digitado = ''.join(filter(str.isdigit, request.POST.get('whatsapp', '')))
            nova_senha = request.POST.get('nova_senha', '').strip()

            user_encontrado = User.objects.filter(username=usuario).first()
            if not user_encontrado:
                contexto['msg_erro'] = '⚠️ Usuário não encontrado! Verifique seu login.'
            else:
                whatsapp_banco = ''.join(filter(str.isdigit, user_encontrado.last_name or ''))
                if whatsapp_digitado and whatsapp_digitado == whatsapp_banco:
                    user_encontrado.set_password(nova_senha)
                    user_encontrado.save()
                    contexto['usuario_confirmado'] = usuario
                    contexto['msg_sucesso'] = f'✓ Senha atualizada com sucesso para {usuario}!'
                else:
                    contexto['msg_erro'] = '⚠️ O WhatsApp informado não confere com o cadastro deste usuário.'
        return render(request, 'redefinir_senha.html', contexto)


# MATRIZ DE URLS DO SISTEMA IMPERIAL:
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pagina_inicial, name='home'),
    path('login/', pagina_login, name='login'),
    path('cadastro/', pagina_cadastro, name='cadastro'),
    path('servicos/', pagina_servicos, name='servicos'),
    path('agendamento/', pagina_agendamento, name='agendamento'),
    path('checkout/', pagina_checkout, name='checkout'),
    path('painel-barbeiro/', pagina_barbeiro, name='painel_barbeiro'),
    path('disparar-zap/<int:agendamento_id>/', disparar_zap, name='disparar_zap'),
    path('reserva-confirmada/', pagina_sucesso, name='pagina_sucesso'),
    path('central-lucros/', central_financeira, name='central_financeira'),
    path('cadastrar-barbeiro/', cadastrar_barbeiro, name='cadastrar_barbeiro'),
    path('fabrica-cupons/', cadastrar_cupom, name='cadastrar_cupom'),
    path('cancelar-corte/<int:agendamento_id>/', cancelar_corte, name='cancelar_corte'),
    path('exportar-caixa/', exportar_caixa, name='exportar_caixa'),
    path('avaliar-corte/<int:agendamento_id>/<int:nota>/', avaliar_corte, name='avaliar_corte'),
    path('manifest.json', manifesto_pwa, name='manifesto_pwa'),
    path('sw.js', service_worker_pwa, name='service_worker_pwa'),
    path('icone_app.png', icone_app_pwa, name='icone_app_pwa'),
    path('gerenciar-servicos/', gerenciar_servicos, name='gerenciar_servicos'),
    path('confirmar-pagamento/<int:agendamento_id>/', confirmar_pagamento, name='confirmar_pagamento'),
    path('redefinir-senha/', pagina_redefinir_senha, name='redefinir_senha'),

]
