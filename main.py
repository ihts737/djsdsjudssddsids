import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    port = int(os.getenv("PORT", 8080))  
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

raid_mode = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def raidhelp(ctx):
    global raid_mode
    raid_mode = not raid_mode
    status = "activated" if raid_mode else "deactivated"
    await ctx.send(f"Raid mode is now {status}.")

@bot.event
async def on_member_join(member):
    if raid_mode:
        try:
            await member.ban(reason="Automatic ban due to raid mode.")
            print(f"Banned {member.name}#{member.discriminator}")
        except Exception as e:
            print(f"Failed to ban {member.name}#{member.discriminator}: {e}")

@bot.event
async def on_invite_create(invite):
    if raid_mode:
        try:
            await invite.delete(reason="Automatic invite revoke due to raid mode.")
            print(f"Revoked invite {invite.url}")
        except Exception as e:
            print(f"Failed to revoke invite {invite.url}: {e}")

bot.run(os.getenv('DISCORD_TOKEN'))
