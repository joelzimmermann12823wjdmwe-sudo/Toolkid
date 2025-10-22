from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    # Gunicorn startet den Webserver stabil im Hintergrund
    os.system(f"gunicorn --bind 0.0.0.0:{port} keep_alive:app") 
    
def keep_alive():
    t = Thread(target=run)
    t.start()