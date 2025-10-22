import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
from keep_alive import keep_alive 
from dotenv import load_dotenv

# Lade Umgebungsvariablen (lokal aus .env, bei Render aus den Einstellungen)
load_dotenv() 
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
REPORT_WEBHOOK_URL = os.getenv("REPORT_WEBHOOK_URL")

# Intents und Bot-Klasse
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

class ToolkidBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.locales = {}
        self.ban_log = {} 
        self.kick_log = {}
        self.report_webhook_url = REPORT_WEBHOOK_URL 

    def load_locales(self):
        print("Lade Sprachdateien...")
        for filename in os.listdir('./locales'):
            if filename.endswith('.json'):
                lang_code = filename[:-5]
                with open(f'./locales/{filename}', 'r', encoding='utf-8') as f:
                    self.locales[lang_code] = json.load(f)

    def get_lang_text(self, lang_code, key, *args):
        text = self.locales.get(lang_code, self.locales.get('en', {})).get(key, f"MISSING_TEXT:{key}")
        return text.format(*args)

    async def setup_hook(self):
        # Lade Cogs (Commands)
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                await self.load_extension(f'commands.{filename[:-3]}')
        
        # Synchronisiere Slash Commands (sehr wichtig!)
        await self.tree.sync()
        
        # Starte den stündlichen Report
        self.hourly_report.start()
        print("Bot ist bereit.")

    @tasks.loop(hours=1.0)
    async def hourly_report(self):
        """Sendet einen stündlichen Bericht über einen Webhook."""
        
        total_bans = sum(self.ban_log.values())
        total_kicks = sum(self.kick_log.values()) 

        lang = 'de' # Für den Report nutzen wir Deutsch
        
        embed = discord.Embed(
            title=self.get_lang_text(lang, "BAN_REPORT_TITLE"),
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name=self.get_lang_text(lang, "REPORT_FIELD_BANS"), value=f"**{total_bans}**", inline=True)
        embed.add_field(name=self.get_lang_text(lang, "REPORT_FIELD_KICKS"), value=f"**{total_kicks}**", inline=True)
        embed.add_field(name="Server geschützt", value="Ja", inline=True) 
        embed.set_footer(text=self.get_lang_text(lang, "REPORT_FOOTER", datetime.now().strftime("%H:%M")))
        
        try:
            # Stelle sicher, dass der Webhook über URL zugänglich ist (kein ctx.send)
            webhook = discord.Webhook.from_url(self.report_webhook_url, client=self)
            await webhook.send(embed=embed, username="Toolkid Report System")
            
            # Logs zurücksetzen
            self.ban_log = {}
            self.kick_log = {}
            
        except Exception as e:
            print(f"FEHLER beim Senden des Webhooks: {e}")

    @hourly_report.before_loop
    async def before_hourly_report(self):
        await self.wait_until_ready()

# --- Bot-Start ---
if __name__ == "__main__":
    if not DISCORD_TOKEN or not REPORT_WEBHOOK_URL:
        print("FEHLER: DISCORD_TOKEN oder REPORT_WEBHOOK_URL nicht gefunden!")
    else:
        bot = ToolkidBot()
        bot.load_locales()
        keep_alive() # Starte Webserver für 24/7
        bot.run(DISCORD_TOKEN)