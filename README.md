# 👑 BarberShop Premium — Sistema ERP & Gestão Inteligente (PWA)

🌐 **Acesse o Sistema Online:** [https://mariaconceicao.pythonanywhere.com](https://mariaconceicao.pythonanywhere.com)

Sistema ERP completo desenvolvido em **Python** e **Django** para a gestão ponta a ponta de barbearias modernas. Conecta a jornada de agendamento do cliente, a operação diária dos barbeiros e o controle financeiro em tempo real da administração em uma única plataforma responsiva com interface *Dark Neon* e suporte a **PWA (Progressive Web App)**.

---

## 🚀 Principais Funcionalidades

### ✂️ Portal do Cliente (`/servicos/` e `/checkout/`)
* **Alistamento Inteligente & Segurança:** Cadastro rápido com preenchimento automático na tela de login, prevenção de duplicidades, atualização de perfil (`/atualizar-cadastro/`) e redefinição de senha validada via WhatsApp (`/redefinir-senha/`).
* **Agendamento Inteligente com Trava de Horário:** Seleção dinâmica do profissional desejado, bloqueio automático de conflitos de dia/horário e trava contra datas ou horários já expirados, com edição rápida de data e horário direto no checkout.
* **Carteira de Cashback Integrada:** Abatimento de saldo acumulado diretamente no checkout e bônus automático de 10% sobre os serviços realizados.
* **Cupons Promocionais Interativos:** Lista suspensa no checkout exibindo os cupons ativos e aplicando o desconto instantaneamente.
* **Histórico, Avaliação & Autoatendimento:** Consulta de cortes realizados, avaliação interativa de 1 a 5 estrelas (`★`) e opção de cancelamento com liberação imediata da agenda.

### 🪒 Painel do Profissional (`/painel-barbeiro/`)
* **Agenda Individualizada:** Exibição filtrada dos clientes e horários marcados para o profissional logado.
* **Controle & Baixa de Pagamentos:** Confirmação rápida de recebimentos realizados no balcão (PIX, Cartão ou Dinheiro), sincronizada com a Central Financeira.
* **Disparador de Lembretes via WhatsApp:** Botão de notificação com um clique que abre o WhatsApp com a mensagem personalizada contendo o nome do cliente, serviço, data e horário.

### 📊 Painel de Bordo Imperial — Administração (`/central-lucros/`)
* **Auditoria Financeira Líquida Real:** Cálculo automático de Faturamento Bruto, Descontos/Cupons aplicados e Lucro Líquido Real.
* **Auditoria Fiscal de Cupons:** Histórico completo dos resgates com diferenciação visual em tempo real entre atendimentos confirmados (`✓ Pago`) e pendentes no balcão (`⏳ A Pagar`).
* **Bases Oficiais Numeradas:** Controle completo de Clientes e Profissionais cadastrados com numeração automática, métricas individuais e edição direta de cadastro pela administração.
* **Filtro por Profissional & Demanda Semanal:** Acompanhamento individual do faturamento por barbeiro e gráfico de volume por dia da semana.
* **Meta Mensal com Barra de Progresso:** Indicador visual dinâmico mostrando a porcentagem atingida (`META ATINGIDA COM SUCESSO!`) e o valor restante para a meta do mês.
* **Selo de Satisfação Média:** Cálculo em tempo real da nota média atribuída pelos clientes (`⭐ 1,0 a 5,0`).
* **Fábrica de Cupons, Catálogo & Credenciamento:** Criação e edição de cupons promocionais e serviços sem mexer no código, além de cadastro de novos profissionais com trava contra logins duplicados.
* **Exportação de Relatórios:** Download instantâneo da planilha completa de caixa em formato `.csv` compatível com Microsoft Excel e Google Sheets.

### 📱 Progressive Web App (PWA)
* Configurado com `manifest.json` e ícones dedicados, permitindo instalar o sistema diretamente na tela inicial do **Android** e **iOS** como um aplicativo nativo.

---

## 🛠️ Tecnologias Utilizadas

* **Back-end:** Python 3.11 & Django
* **Front-end:** HTML5, CSS3 (Dark Mode & Neon UI responsivo) e JavaScript
* **Banco de Dados:** SQLite3 (Django ORM)
* **Integrações & Infraestrutura:** API Web do WhatsApp (`wa.me`), geração nativa de planilhas CSV, Git, GitHub e PythonAnywhere

---

## ⚙️ Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com
   cd barbershop-premium
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   ```

3. **Instale as dependências e aplique as migrações:**
   ```bash
   pip install django
   python manage.py migrate
   ```

4. **Inicie o servidor local:**
   ```bash
   python manage.py runserver
   ```
   Acesse no navegador: `http://127.0.0`

---

## 👩‍💻 Autoria

Desenvolvido por **Conceição** (`@Conceicao-creator`).
