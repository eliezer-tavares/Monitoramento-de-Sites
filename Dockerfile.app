FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Define as variáveis de ambiente - these will be overridden by docker-compose.yaml
ENV SMTP_SERVER=smtp.gmail.com
ENV SMTP_PORT=587
ENV SMTP_USERNAME=seu_email@gmail.com
ENV SMTP_PASSWORD=sua_senha
ENV RECIPIENT_EMAIL=email_para_receber_alertas@gmail.com
ENV TELEGRAM_BOT_TOKEN=seu_token_do_bot
ENV TELEGRAM_CHAT_ID=seu_chat_id
ENV CHECK_INTERVAL=10

CMD ["python", "main.py"]
