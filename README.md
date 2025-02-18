Monitor de Disponibilidade de Sites

Este projeto é um monitor de disponibilidade de sites que verifica periodicamente o status de uma lista de sites e envia alertas por e-mail e Telegram (opcional) caso algum site fique offline. O sistema foi desenvolvido em Python, utilizando asyncio para verificações assíncronas, Flask para fornecer uma API REST e um frontend simples em HTML/JavaScript para visualização do status. Os dados de status são armazenados em um banco de dados SQLite para análise histórica.

Funcionalidades
• Monitoramento assíncrono de múltiplos sites.
• Alertas por e-mail via SMTP.
• Alertas opcionais via Telegram.
• Armazenamento do histórico de disponibilidade em um banco de dados SQLite.
• API REST para acesso aos dados de status.
• Interface web simples para visualização em tempo real.
• Configuração flexível via arquivo .env.
• Dockerizado para fácil implantação.

Como Executar
1. Clone o repositório:
git clone https://github.com/eliezer-tavares/monitoramento-de-sites.git
cd monitoramento-de-sites
2. Configure o ambiente:
Crie um arquivo .env com base no modelo fornecido:
cp .env.example .env
Edite o arquivo .env com suas credenciais de e-mail, Telegram (opcional) e outras configurações.
3. Inicie o projeto com Docker Compose:
docker-compose up -d --build
4. Acesse a interface web:
Abra seu navegador e acesse:
http://localhost:8000
5. Acesse a API REST:
A API REST pode ser acessada via:
http://localhost:8000/api/status
Configuração
As configurações do projeto são definidas no arquivo .env. As seguintes variáveis de ambiente podem ser configuradas:
Variável
Descrição
API_URL
URL da API REST (padrão: http://localhost:8000)
SMTP_SERVER
Servidor SMTP para envio de emails
SMTP_PORT
Porta SMTP
SMTP_USERNAME
Nome de usuário SMTP
SMTP_PASSWORD
Senha SMTP
RECIPIENT_EMAIL
E-mail para receber os alertas
TELEGRAM_BOT_TOKEN
Token do bot do Telegram (opcional)
TELEGRAM_CHAT_ID
ID do chat do Telegram para alertas (opcional)
CHECK_INTERVAL
Intervalo entre verificações (em segundos)
Tecnologias Utilizadas
• 
Backend: Python, Flask, FastAPI, Uvicorn, Asyncio, Requests, Aiosmtplib, Python-dotenv
• 
Banco de Dados: SQLite
• 
Infraestrutura: Docker, Docker Compose
• 
Frontend: HTML, JavaScript

Melhorias Futuras
• 
Implementação de testes unitários.
• 
Adição de mais opções de notificação (Slack, Discord, etc.).
• 
Sistema de login/autenticação para a interface web e API.
• 
Melhoria na interface web com mais recursos e visualizações.

Autor
Eliezer Tavares de Oliveira

E-mail
eliezertavaresdeoliveira@gmail.com
