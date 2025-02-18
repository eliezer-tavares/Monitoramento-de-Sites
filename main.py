import asyncio
import json
import logging
import sqlite3
import os
from datetime import datetime

import aiosmtplib
import requests
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do email
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Configurações do Telegram (opcional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Banco de dados SQLite
DATABASE_NAME = "site_monitor.db"

# Intervalo de verificação padrão (em segundos)
DEFAULT_CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000") # Default para desenvolvimento local

def setup_database():
  """Cria a tabela de logs no banco de dados se ela não existir."""
  conn = sqlite3.connect(DATABASE_NAME)
  cursor = conn.cursor()
  cursor.execute("""
      CREATE TABLE IF NOT EXISTS site_availability_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          site_url TEXT NOT NULL,
          status_code INTEGER,
          response_time_ms INTEGER,
          is_online BOOLEAN NOT NULL
      )
  """)
  conn.commit()
  conn.close()

def load_sites_from_json(filepath="sites.json"):
  """Carrega a lista de sites a serem monitorados de um arquivo JSON."""
  try:
    with open(filepath, "r") as f:
      sites = json.load(f)
      return sites
  except FileNotFoundError:
    logging.error(f"Arquivo de configuração {filepath} não encontrado.")
    return []
  except json.JSONDecodeError:
    logging.error(f"Erro ao decodificar o JSON no arquivo {filepath}. Verifique a sintaxe.")
    return []

def log_site_status(site_url, status_code, is_online, response_time_ms):
    """Logs the site status to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO site_availability_logs (site_url, status_code, is_online, response_time_ms)
        VALUES (?, ?, ?, ?)
    """, (site_url, status_code, is_online, response_time_ms))
    conn.commit()
    conn.close()

async def send_email(subject, message):
  """Envia um email de alerta."""
  email_message = f"Subject: {subject}\n\n{message}"
  try:
    await aiosmtplib.send(
        email_message,
        from_addr=SMTP_USERNAME,
        to_addrs=[RECIPIENT_EMAIL],
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        starttls=True,
    )
    logging.info(f"Email sent to {RECIPIENT_EMAIL} with subject: {subject}")
  except Exception as e:
    logging.error(f"Failed to send email: {e}")

async def send_telegram_message(message):
    """Sends a Telegram message if Telegram integration is configured."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram bot token or chat ID not configured. Skipping Telegram message.")
        return

    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(telegram_api_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        logging.info("Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")

async def check_site(site):
  """Verifica o status de um site e envia alertas se estiver offline."""
  url = site['url']
  try:
    start_time = datetime.now()
    response = requests.get(url, timeout=20) # Aumentando o timeout para 20 segundos
    end_time = datetime.now()
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
    status_code = response.status_code
    is_online = status_code >= 200 and status_code < 300

    log_site_status(url, status_code, is_online, response_time_ms)

    if not is_online:
      logging.warning(f"Site {url} está offline. Status code: {status_code}")
      await send_email(
          f"ALERTA: Site {url} Offline",
          f"O site {url} está offline. Status code: {status_code}. Verifique imediatamente."
      )
      await send_telegram_message(f"ALERTA: Site {url} Offline! Status code: {status_code}")

    else:
        logging.info(f"Site {url} está online. Status code: {status_code}, Response time: {response_time_ms}ms")

    return {"url": url, "status_code": status_code, "is_online": is_online, "response_time_ms": response_time_ms}

  except requests.exceptions.RequestException as e:
    logging.error(f"Erro ao verificar {url}: {e}")
    log_site_status(url, None, False, None)
    await send_email(
        f"ALERTA: Erro ao verificar {url}",
        f"Erro ao verificar o site {url}: {e}. Verifique a conexão ou a configuração do site."
    )
    await send_telegram_message(f"ALERTA: Erro ao verificar {url}: {e}")
    return {"url": url, "status_code": None, "is_online": False, "response_time_ms": None}
  except Exception as e:
    logging.error(f"Erro inesperado ao verificar {url}: {e}")
    log_site_status(url, None, False, None)
    await send_email(
        f"ALERTA: Erro ao verificar {url}",
        f"Erro ao verificar o site {url}: {e}. Verifique a conexão ou a configuração do site."
    )
    await send_telegram_message(f"ALERTA: Erro ao verificar {url}: {e}")
    return {"url": url, "status_code": None, "is_online": False, "response_time_ms": None}

async def monitor_sites(sites, check_interval=DEFAULT_CHECK_INTERVAL):
  """Monitora os sites a cada intervalo de tempo."""
  while True:
    logging.info("Verificando sites...")
    tasks = [check_site(site) for site in sites]
    results = await asyncio.gather(*tasks)
    # Envia os resultados para a API
    await send_status_to_api(results)
    logging.info(f"Próxima verificação em {check_interval} segundos.")
    await asyncio.sleep(check_interval)

async def send_status_to_api(results):
  """Envia o status dos sites para a API."""
  try:
    api_url = f"{API_URL}/api/update_status"  # Ajuste a URL conforme necessário
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(results)
    response = requests.post(api_url, headers=headers, data=data)
    response.raise_for_status()
    logging.info("Status enviado para a API com sucesso.")
  except requests.exceptions.RequestException as e:
    logging.error(f"Erro ao enviar status para a API: {e}")

async def main():
  """Função principal para iniciar o monitoramento."""
  setup_database()
  sites = load_sites_from_json()

  if not sites:
    logging.error("Nenhum site configurado para monitorar. Saindo.")
    return

  await monitor_sites(sites)

if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    logging.info("Monitoramento interrompido pelo usuário.")