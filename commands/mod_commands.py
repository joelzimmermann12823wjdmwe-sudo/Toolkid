import discord
from discord.ext import commands
from discord import app_commands # Für Slash Commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_text(self, guild_id, key, *args):
        # Hier sollte später die Sprach-ID des Servers abgerufen werden
        lang = 'de' 
        return self.bot.get_lang_text(lang, key, *args)

    # ----------------------------------------------------------------
    # HELLO BEFEHL: Prefix Command (!hallo)
    @commands.command(name="hallo")
    async def hello_prefix(self, ctx: commands.Context):
        text = self.get_text(ctx.guild.id, "GREETING", ctx.author.display_name)
        await ctx.send(text)

    # HELLO BEFEHL: Slash Command (/hallo)
    @app_commands.command(name="hallo", description="Sagt Hallo zum Benutzer")
    async def hello_slash(self, interaction: discord.Interaction):
        text = self.get_text(interaction.guild_id, "GREETING", interaction.user.display_name)
        await interaction.response.send_message(text, ephemeral=True) # ephemeral=True: Nur der Nutzer sieht die Antwort

    # ----------------------------------------------------------------
    # BAN BEFEHL: Prefix Command (!ban)
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx: commands.Context, member: discord.Member, *, reason="No reason"):
        # DUMMY-LOGIK
        if ctx.guild.id not in self.bot.ban_log:
            self.bot.ban_log[ctx.guild.id] = 0
        self.bot.ban_log[ctx.guild.id] += 1
        
        text = self.get_text(ctx.guild.id, "SUCCESSFUL_BAN", member.display_name)
        await ctx.send(text)

    # BAN BEFEHL: Slash Command (/ban)
    @app_commands.command(name="ban", description="Bannt einen Benutzer vom Server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        # DUMMY-LOGIK
        if interaction.guild_id not in self.bot.ban_log:
            self.bot.ban_log[interaction.guild_id] = 0
        self.bot.ban_log[interaction.guild_id] += 1
        
        text = self.get_text(interaction.guild_id, "SUCCESSFUL_BAN", member.display_name)
        await interaction.response.send_message(text, ephemeral=True) 

async def setup(bot):
    await bot.add_cog(Moderation(bot))