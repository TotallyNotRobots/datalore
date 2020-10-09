"""
bot.py - the brains behind Datalore.
(C) 2020 J.C. Boysha
    This file is part of Datalore.

    Datalore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Datalore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Datalore.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

IMG_URL = (
    "https://vignette.wikia.nocookie.net/zimwiki/images/1/19/"
    "Hunter_Destroyer_Machine.png/revision/latest/"
    "scale-to-width-down/340?cb=20130307023703"
)

load_dotenv()


STATS = os.getenv("STA_STATS")
GSTATS = os.getenv("GAME_STATS")
SCORES = os.getenv("SCORES")
URL = os.getenv("URL_PATH")

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


TOKEN = os.getenv("DISCORD_TOKEN")
client = commands.Bot(command_prefix=os.getenv("COMMAND_PREFIX"))


@client.command
async def load(extension):
    client.load_extension(f"extensions.{extension}")


@client.command
async def unload(extension):
    client.unload_extension(f"extensions.{extension}")


for filename in os.listdir("extensions"):
    if filename.endswith(".py") and not filename.startswith("__"):
        client.load_extension(f"extensions.{filename[:-3]}")


@client.event
async def on_message(message):
    if URL is not None:
        if message.content == "WHAT IS IT?!":
            embed = discord.Embed(title="A HUNTER DESTROYER MACHINE")
            embed.set_image(url=IMG_URL)
            await message.channel.send(embed=embed)
        if message.content == "Plain, Simple, Garak.":
            embed = discord.Embed(title="A Simple Tailor")
            embed.set_image(url=URL + "Garak.jpg")
            await message.channel.send(embed=embed)
        await client.process_commands(message)


client.run(TOKEN)
