import os
import requests
from bs4 import BeautifulSoup
import urllib3
import datetime
import telebot
from dotenv import load_dotenv

# Configuración inicial
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(TOKEN)

def get_bcv_rate():
    url = "https://www.bcv.org.ve/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rate_text = soup.find('div', id='dolar').find('strong').text.strip()
        return float(rate_text.replace(',', '.'))
    except Exception as e:
        print(f"Error BCV: {e}")
        return None

def get_binance_p2p(amount):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": True,
        "page": 1,
        "payTypes": ["PagoMovil"],
        "publisherType": "merchant",
        "rows": 1,
        "tradeType": "SELL",
        "transAmount": str(int(amount))
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if data.get('success'):
            return float(data['data'][0]['adv']['price'])
        return None
    except Exception as e:
        print(f"Error Binance: {e}")
        return None

def ejecutar_consulta():
    bcv = get_bcv_rate()
    if not bcv: return
    
    binance = get_binance_p2p(bcv * 10)
    
    if binance:
        gap = ((binance - bcv) / bcv) * 100
        factor = bcv / binance # <-- El factor que pediste
        ahora = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
        
        texto = (
            f"📊 *REPORTE DE TASAS*\n"
            f"📅 {ahora}\n\n"
            f"🏛 *BCV:* {bcv:.2f} VES\n"
            f"🔸 *Binance:* {binance:.2f} VES\n"
            f"📈 *Brecha:* {gap:.2f}%\n"
            f"🔄 *Factor:* {factor:.4f}"
        )
        
        bot.send_message(CHAT_ID, texto, parse_mode="Markdown")
        print("Reporte enviado a Telegram con éxito.")
    else:
        print("No se pudo obtener la tasa de Binance.")

if __name__ == "__main__":
    ejecutar_consulta()