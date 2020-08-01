# bot2.py
# For learning and shit

import os, discord, json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()


STATS = os.getenv('STA_STATS')
GSTATS = os.getenv('GAME_STATS')
SCORES = os.getenv('SCORES')

try: 
    with open(STATS) as stats:
        json.load(stats)
except: 
    setStats = {}
    with open(STATS, "w") as stats:
        json.dump(setStats, stats)

try:
    with open(SCORES) as stats:
        json.load(stats)
except: 
    setStats = {}
    with open(SCORES, "w") as stats:
        json.dump(setStats, stats)
        

TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = os.getenv('COMMAND_PREFIX'))

@client.command
async def load(ctx, extension):
    client.load_extension(f'extensions.{extension}')

@client.command
async def unload(ctx, extension):
    client.unload_extension(f'extensions.{extension}')

for filename in os.listdir('extensions'):
    if filename.endswith('.py'):
        client.load_extension(f'extensions.{filename[:-3]}')

@client.event
async def on_message(message):
    if message.content == "WHAT IS IT?!":
        embed = discord.Embed(title="A HUNTER DESTROYER MACHINE")
        embed.set_image(url="https://vignette.wikia.nocookie.net/zimwiki/images/1/19/Hunter_Destroyer_Machine.png/revision/latest/scale-to-width-down/340?cb=20130307023703")
        await message.channel.send(embed=embed)
    await client.process_commands(message)

client.run(TOKEN)