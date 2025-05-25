# Focus Lab - Seu Assistente Pessoal de Foco e Produtividade

Focus Lab é uma aplicação web desenvolvida para ajudar usuários a gerenciar seu dia a dia, organizar tarefas, tomar notas e melhorar a gestão do tempo com ferramentas como Timer e Pomodoro.

## ✨ Funcionalidades Principais

* **Autenticação de Usuários:** Sistema seguro de registro e login.
* **Dashboard Diário Dinâmico:**
    * Visualização de notas e tarefas para qualquer data selecionada.
    * Navegação fácil entre dia anterior, dia seguinte e retorno rápido para o dia atual (clicando no logo).
* **Gerenciamento de Notas:** Crie e atualize notas contextuais para cada dia.
* **Gerenciamento de Tarefas:**
    * Adicione tarefas com nomes e cores personalizadas para cada dia.
    * Marque tarefas como concluídas/não concluídas.
    * Delete tarefas.
* **Perfil de Usuário Personalizável:**
    * Visualize e atualize o primeiro nome.
    * Atualize a foto de perfil com uploads personalizados ou use uma foto padrão aleatória atribuída no registro.
* **Agenda/Calendário Interativo:**
    * Visualize um calendário anual completo.
    * Navegue para o dashboard de qualquer dia clicando na data no calendário.
    * Botão "Voltar" inteligente que retorna ao dashboard da data previamente visualizada.
* **Ferramenta de Timer Integrada:**
    * **Modo Timer Padrão:** Defina uma contagem regressiva com duração personalizável (em minutos), com botões de Iniciar, Pausar, Continuar e Resetar.
    * **Modo Pomodoro:** Ciclos configurados de Foco, Pausa Curta e Pausa Longa para otimizar a produtividade, com botões de Iniciar, Pausar, Continuar, Pular Fase e Resetar Ciclos.
    * Interface clara com exibição do tempo restante e do status/fase atual.
    * O título da aba do navegador é atualizado dinamicamente com o tempo restante.
* **Navegação Intuitiva:** Barra lateral com acesso rápido à Agenda.

## 🛠️ Tecnologias Utilizadas

* **Backend:**
    * Python
    * Flask (Framework web)
    * Flask-SQLAlchemy (ORM para interação com banco de dados)
    * Werkzeug (Para hashing de senhas e segurança de arquivos)
    * pytz (Para manipulação de fusos horários)
* **Frontend:**
    * HTML5
    * CSS3
    * JavaScript (Para lógica do Timer/Pomodoro e interatividade)
    * Jinja2 (Template engine do Flask)
* **Banco de Dados:**
    * SQLite (Banco de dados leve baseado em arquivo)

## 🚀 Começando

Siga estas instruções para configurar e rodar o projeto localmente.

### Pré-requisitos

* Python 3.7+
* pip (gerenciador de pacotes do Python)
* Git

### Instalação

1.  **Crie e ative um ambiente virtual (recomendado):**
    * No Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * No macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Rodando a Aplicação

1.  **Execute o script principal:**
    ```bash
    python main.py
    ```
2.  Abra seu navegador e acesse: `http://localhost:5000/`

A aplicação deverá estar rodando! O arquivo de banco de dados `dados.db` será criado automaticamente na primeira vez que a aplicação for executada e precisar interagir com o banco.
