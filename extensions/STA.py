'''
STA - A COG Module for the Datalore Discord bot
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
'''
import os, discord, csv, random, asyncio, json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

STATS = os.getenv('STA_STATS')
GSTATS = os.getenv('GAME_STATS')
URL=os.getenv('URL_PATH')

class STA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def player_embed(self, ctx):
        pstats = {}
        player = ctx.author.name
        with open(STATS) as stats: 
            statset = json.load(stats)
            pstats = statset[player]

        embed = discord.Embed(
            title=pstats["Name"],
            description=pstats["Race"],
            colour = discord.Colour.blue()
        )

        current = pstats
        attributes = current["Attributes"]
        disciplines = current["Disciplines"]
        if URL!=None and URL!="":
            embed.set_author(name = player, icon_url=URL+"Commbadge.png")
        else:
            embed.set_author(name = player)
        embed.add_field(name="Stress", value = pstats["Stress"], inline=True)
        embed.add_field(name="Determination", value=pstats["Determination"], inline=True)
        embed.add_field(name="Attributes", value="---", inline=False)
        embed.add_field(name="Control", value=attributes["Control"], inline=True)
        embed.add_field(name="Fitness", value=attributes["Fitness"], inline=True)
        embed.add_field(name="Presence", value=attributes["Presence"], inline=True)
        embed.add_field(name="Daring", value=attributes["Daring"], inline=True)
        embed.add_field(name="Insight", value=attributes["Insight"], inline=True)
        embed.add_field(name="Reason", value=attributes["Reason"], inline=True)
        embed.add_field(name="Disciplines", value="---", inline=False)
        embed.add_field(name="Command", value=disciplines["Command"])
        embed.add_field(name="Security", value=disciplines["Security"])
        embed.add_field(name="Science", value=disciplines["Science"])
        embed.add_field(name="Conn", value=disciplines["Conn"])        
        embed.add_field(name="Engineering", value=disciplines["Engineering"])
        embed.add_field(name="Medicine", value=disciplines["Medicine"])

        await ctx.send(embed=embed)

    @commands.command(name="dmg", help="Roll Damage.")
    async def damage(self, ctx, dicePool:int):
        rolls = []
        dmg = 0
        fx = 0
        for i in range(0, dicePool):
            rolls.append(random.randint(1,6))
        
        for roll in rolls: 
            if roll == 1:
                dmg +=1
            elif roll == 2:
                dmg += 2
            elif roll == 5:
                dmg += 1
                fx += 1
            elif roll == 6:
                dmg += 1
                fx += 1
        
        embed=discord.Embed(
            title="Damage Result",
            colour = discord.Colour.magenta()
        )
        embed.add_field(name="Damage: ", value=dmg)
        embed.add_field(name="Effects: ", value=fx)
        embed.add_field(name="Rolls: ", value=str(rolls), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="game_stats", help="View and Modify current Game Stats")
    async def gameStats(self, ctx, op="get", stat=None, value=0, send=True, color=discord.Colour.gold()):
        try:
            with open(GSTATS + '.' + ctx.channel.name + '.json') as stats: 
                gstats = {}
                try:
                     gstats = json.load(stats)
                     if gstats["Momentum"] > 6:
                        gstats["Momentum"] = 6
                except: 
                    gstats = {}
                    gstats["Momentum"] = 0
                    gstats["Threat"] = 0
                    with open(GSTATS + '.' + ctx.channel.name + '.json', "w") as stats:
                        json.dump(gstats, stats)
        except:
            with open(GSTATS + '.' + ctx.channel.name + '.json', "w+") as stats: 
                gstats = {}
                try:
                    gstats = json.load(stats)
                    if gstats["Momentum"] > 6:
                        gstats["Momentum"] = 6
                    if gstats["Threat"] > 10:
                        gstats["Threat"] = 10
                except: 
                    gstats = {}
                    gstats["Momentum"] = 0
                    gstats["Threat"] = 0
                    with open(GSTATS + '.' + ctx.channel.name + '.json', "w") as stats:
                        json.dump(gstats, stats)

        if op == "get":
            embed = discord.Embed(title="Game Stats", 
                                  description = f'***{ctx.channel.name}***  Threat and Momentum', 
                                  colour = color)
            
            embed.add_field(name="Momentum", value=gstats["Momentum"])
            embed.add_field(name="Threat", value=gstats["Threat"])

            await ctx.send(embed=embed)

        elif op == "sub":
            try:
                gstats[stat] -= value
                with open(GSTATS + '.' + ctx.channel.name + '.json', "w") as stats:
                    json.dump(gstats, stats)
                if send:
                    await self.gameStats(ctx, "get", color = discord.Colour.magenta())
            except:
                await ctx.send("Something about that was not right. Does that Stat exist?")
        
        elif op == "add":
            try:
                gstats[stat] += value
                with open(GSTATS + '.' + ctx.channel.name + '.json', "w") as stats:
                    json.dump(gstats, stats)
                if send:
                    await self.gameStats(ctx, "get", color = discord.Colour.green())
            except:
                await ctx.send("Something about that was not right. Does that Stat exist?")

        else:
            await ctx.send("Please see the help, I did not understand your command.")
        


    @commands.command(name="get_char", help="View current player Stats.")
    async def getStat(self, ctx):
        await self.player_embed(ctx)

    @commands.command(name="set_stats", help="sets various player stats.")
    async def setStat(self, ctx, stat: str, op: str, value: int):
        setStats = {}
        with open(STATS, "r") as stats:
            player = ctx.message.author.name
            pstats = json.load(stats)

        if op == "set":
            if stat.lower() in ["det", "determination"]:
                pstats[player]["Determination"] = value

            elif stat.lower() in ["stress", "str"]:
                pstats[player]["Stress"] = value
            
        else:
            if op == "add":
                change = value
            if op == "sub":
                change = -value

            if stat.lower() in ["det", "determination"]:
                pstats[player]["Determination"] += change

            elif stat.lower() in ["stress", "str"]:
                pstats[player]["Stress"] += change

            setStats = pstats
        
        with open(STATS, "w") as stats:
            json.dump(pstats, stats)

        await self.player_embed(ctx)

    @commands.command(name="set_attr", help="sets player attribute to value.")
    async def setAttr(self, ctx, stat: str, value: int):
        setStats = {}        
        with open(STATS, "r") as stats:
            pstats = json.load(stats)
            setStats = pstats[ctx.message.author.name]
        
        try: 
            pstats[ctx.message.author.name]["Attributes"][stat] = value

            setStats = pstats
            with open(STATS, "w") as stats:
                json.dump(pstats, stats)

            await self.player_embed(ctx)
        except: 
            await ctx.send("There was an issue processing. Check that " + str(stat) + " is a valid attribute.")

    @commands.command(name="set_disc", help="sets player discipline to value.")
    async def setDisc(self, ctx, disc: str, value: int):
        setStats = {}               
        with open(STATS, "r") as stats:
            pstats = json.load(stats)
            setStats = pstats[ctx.message.author.name]
        
        try: 
            pstats[ctx.message.author.name]["Disciplines"][disc] = value

            setStats = pstats
            with open(STATS, "w") as stats:
                json.dump(pstats, stats)

            await self.player_embed(ctx)
        except: 
            await ctx.send("There was an issue processing. Check that " + str(disc) + " is a valid discipline.")
            
    @commands.command(name="create_player", help="Creates a Player and Stats.  <more> \n\
    usage: create_player <name> <race> <control> <daring> <fitness> \
    <insight> <presence> <reason> <command> <conn> <security> <engineering> \
    <science> <medicine>")
    async def create_player(self, ctx, name: str, race: str, control: int,
                            daring: int, fitness: int, insight: int,
                            presence: int, reason: int, command: int, 
                            conn: int, security: int, engineering: int, 
                            science: int, medicine: int):
        setStats = {}
        with open(STATS) as stats: 
            pstats = json.load(stats)
            player = ctx.message.author.name
            if player in pstats:
                await ctx.message.channel.send(player + "Already has a Character ("+pstats[player]["Name"]+").")
            else: 
                current = pstats[player] = {}
                attributes = current["Attributes"] = {}
                disciplines = current["Disciplines"] = {}
                current["Name"] = name
                current["Race"] = race
                current["Stress"] = 0
                current["Determination"] = 0
                attributes["Control"] = control
                attributes["Fitness"] = fitness
                attributes["Presence"] = presence
                attributes["Daring"] = daring
                attributes["Insight"] = insight
                attributes["Reason"] = reason
                disciplines["Command"] = command
                disciplines["Security"] = security
                disciplines["Science"] = science
                disciplines["Conn"] = conn
                disciplines["Engineering"] = engineering
                disciplines["Medicine"] = medicine
                await ctx.message.channel.send("Character created!")

            setStats = pstats
        
        with open(STATS, "w") as stats:
            json.dump(pstats, stats)
            
        await self.player_embed(ctx)

    @commands.command(name="Challenge", help="Undertake a challenge. <more> \n usage: Challenge <Attribute> <Discipline> <Difficulty> <dice pool> <Focus>")
    async def challenge(self, ctx, attribute: str, discipline: str, target: int, dicePool: int, focus=False):
        pstats = {}
        player = ctx.author.name
        with open(STATS) as stats: 
            statset = json.load(stats)
            pstats = statset[player]

        attributes = pstats["Attributes"]
        disciplines = pstats["Disciplines"]
        try: 
            attr = attributes[attribute]
        except: 
            await ctx.send("Could not understand: " + str(attribute))
        
        try:
            disc = disciplines[discipline]
        except:
            await ctx.send("Could not understand: " + str(discipline))
        
        challengeValue = int(attr) + int(disc)
        
        # Success, Complication
        scores = [0,0]

        success = False
        complications = False

        rolls = []
        for i in range(0, dicePool):
            rolls.append(random.randint(1,20))
        
        for roll in rolls:
            if roll >= 20:
                scores[1] += 1
            if roll < challengeValue:
                scores[0] += 1
            if focus:
                if roll < disc:
                    scores[0] += 1

        if scores[0] >= target:
            success = True

        else:
            success = False

        if scores[1] > 0:
            complications = True

        if success:
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.green()
            )

        if success and complications:
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.gold()
            )

        if not success: 
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.red()
            )
        embed.add_field(name="difficulty: ", value=target, inline=False)
        embed.add_field(name="Successes: ", value=scores[0])
        embed.add_field(name="Complications: ", value=scores[1])
        embed.add_field(name="Rolls: ", value=str(rolls), inline=True)
        if scores[0] > target:
            momentum = scores[0]-target
            embed.add_field(name="Momentum: ", value=momentum, inline=True)
            await self.gameStats(ctx, op="add", stat="Momentum", value=momentum, send=False)
        if success: 
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Green-alert.gif")
        if success and complications:
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Yellow-alert.gif")
        if not success: 
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Red-alert.gif")

        await ctx.send(embed=embed)

    @commands.command(name="GMChallenge", help="Undertake a challenge. <more> \n usage: Challenge <Attribute> <Attribute Score> <Discipline> <Disciplne Score> <Difficulty> <dice pool> <focus>")
    async def GMchallenge(self, ctx, attribute: str, attr: int, discipline: str, disc: int, target: int, dicePool: int, focus=False):    
        challengeValue = int(attr) + int(disc)
        
        # Success, Complication
        scores = [0,0]

        success = False
        complications = False

        rolls = []
        for i in range(0, dicePool):
            rolls.append(random.randint(1,20))
        
        for roll in rolls:
            if roll >= 20:
                scores[1] += 1
            if roll < challengeValue:
                scores[0] += 1
            if focus:
                if roll < disc:
                    scores[0] += 1

        if scores[0] >= target:
            success = True

        else:
            success = False

        if scores[1] > 0:
            complications = True

        if success:
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.green()
            )

        if success and complications:
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.gold()
            )

        if not success: 
            embed = discord.Embed(
                title="Challenge",
                description=str(discipline) + " + " + str(attribute),
                colour = discord.Colour.red()
            )
        embed.add_field(name="difficulty: ", value=target, inline=False)
        embed.add_field(name="Successes: ", value=scores[0])
        embed.add_field(name="Complications: ", value=scores[1])
        embed.add_field(name="Rolls: ", value=str(rolls), inline=True)
        if scores[0] > target:
            Threat = scores[0]-target
            embed.add_field(name="Threat: ", value=Threat, inline=True)
            await self.gameStats(ctx, op="add", stat="Threat", value=Threat, send=False)
        if success: 
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Green-alert.gif")
        if success and complications:
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Yellow-alert.gif")
        if not success: 
            if URL!=None and URL!="":
                embed.set_image(url=URL+"Red-alert.gif")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(STA(bot))