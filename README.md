# 👑 BarberShop Premium — Sistema ERP & Gestão Inteligente

Sistema ERP completo desenvolvido em **Python** e **Django** para a gestão ponta a ponta de barbearias modernas. Conecta a jornada de agendamento do cliente, a operação diária dos barbeiros e o controle financeiro em tempo real da administração em uma única plataforma com interface *Dark Neon*.

---

## 🚀 Principais Funcionalidades

### ✂️ Portal do Cliente (`/servicos/` e `/checkout/`)
* **Alistamento Inteligente:** Cadastro rápido com preenchimento automático na tela de login e prevenção de duplicidades.
* **Agendamento com Escolha de Profissional:** Seleção dinâmica do barbeiro desejado e bloqueio automático de conflitos de dia e horário.
* **Carteira de Cashback Integrada:** Abatimento de saldo acumulado diretamente no checkout e bônus automático de 10% sobre os serviços realizados.
* **Cupons Promocionais:** Aplicação e validação instantânea de códigos de desconto.
* **Histórico, Avaliação & Autoatendimento:** Consulta de cortes realizados, avaliação interativa de 1 a 5 estrelas (`★`) e opção de cancelamento com liberação imediata da agenda.

### 🪒 Painel do Profissional (`/painel-barbeiro/`)
* **Agenda Individualizada:** Exibição filtrada apenas dos clientes e horários marcados para o barbeiro logado.
* **Disparador de Lembretes via WhatsApp:** Botão de notificação com um clique que abre o WhatsApp com a mensagem personalizada contendo o nome do cliente, serviço, data e horário.

### 📊 Painel de Bordo Imperial — Administração (`/central-lucros/`)
* **Auditoria Financeira Líquida Real:** Cálculo automático de Faturamento Bruto, Descontos/Cupons aplicados e Lucro Líquido Real.
* **Filtro por Profissional:** Acompanhamento individual do faturamento e desempenho de cada barbeiro da rede.
* **Meta Mensal com Barra de Progresso:** Indicador visual dinâmico mostrando a porcentagem atingida e o valor restante para bater a meta do mês.
* **Selo de Satisfação Média:** Cálculo em tempo real da nota média atribuída pelos clientes (`⭐ 1,0 a 5,0`).
* **Fábrica de Cupons & Credenciamento:** Criação de novos cupons promocionais e cadastro de novos profissionais com trava contra nomes duplicados.
* **Exportação de Relatórios:** Download instantâneo da planilha completa de caixa em formato `.csv` compatível com Microsoft Excel.

---

## 🛠️ Tecnologias Utilizadas

* **Back-end:** Python 3.11 & Django
* **Front-end:** HTML5, CSS3 (Dark Mode & Neon UI) e JavaScript
* **Banco de Dados:** SQLite3 (Django ORM)
* **Integrações:** API Web do WhatsApp (`wa.me`) e geração nativa de planilhas CSV

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
