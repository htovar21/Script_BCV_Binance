import os
import requests
from bs4 import BeautifulSoup
import urllib3
import datetime
import pytz  # <--- Nueva importación
import telebot
from dotenv import load_dotenv

# ... (las funciones get_bcv_rate y get_binance_p2p se quedan igual)

def ejecutar_consulta():
    bcv = get_bcv_rate()
    if not bcv: return
    
    binance = get_binance_p2p(bcv * 10)
    
    if binance:
        gap = ((binance - bcv) / bcv) * 100
        factor = bcv / binance
        
        # --- AJUSTE DE HORA VENEZUELA ---
        zona_horaria = pytz.timezone('America/Caracas')
        ahora = datetime.datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")
        # --------------------------------
        
        texto = (
            f"📊 *REPORTE DE TASAS*\n"
            f"📅 {ahora}\n\n"
            f"🏛 *BCV:* {bcv:.2f} VES\n"
            f"🔸 *Binance:* {binance:.2f} VES\n"
            f"📈 *Brecha:* {gap:.2f}%\n"
            f"🔄 *Factor:* {factor:.4f}"
        )
        
        bot.send_message(CHAT_ID, texto, parse_mode="Markdown")
        print(f"Reporte enviado con hora local: {ahora}")