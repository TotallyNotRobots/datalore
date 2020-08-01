# bot.py
import os, discord, csv, random, asyncio, json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')
STATS = os.getenv('STA_STATS')
SCORES = os.getenv('SCORES')
TRIVIA = os.getenv('TRIVIA')

client = discord.Client()
bot = commands.Bot(command_prefix=COMMAND_PREFIX)

async def player_embed(ctx):
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

    embed.set_author(name = player, icon_url="https://jcboysha.com/STA/Commbadge.png")
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
    embed.add_field(name="Conn", value=disciplines["Conn"])
    embed.add_field(name="Security", value=disciplines["Security"])
    embed.add_field(name="Engineering", value=disciplines["Engineering"])
    embed.add_field(name="Science", value=disciplines["Science"])
    embed.add_field(name="Medicine", value=disciplines["Medicine"])

    await ctx.send(embed=embed)

@bot.command(name="dmg", help="Roll Damage.")
async def damage(ctx, dicePool:int):
    rolls = []
    dmg = 0
    fx = 0
    for i in range(0, dicePool):
        rolls.append(random.randint(1,7))
    
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

@bot.command(name="Challenge", help="Undertake a challenge. <more> \n usage: Challenge <Attribute> <Discipline> <Difficulty> <dice pool>")
async def challenge(ctx, attribute: str, discipline: str, target: int, dicePool: int):
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
        rolls.append(random.randint(1,21))
    
    for roll in rolls:
        if roll >= 20:
            scores[1] += 1
        if roll < challengeValue:
            scores[0] += 1
        if roll < disc:
            scores[0] += 1

    if scores[0] > target:
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
        embed.add_field(name="Momentum: ", value=scores[0]-target, inline=True)
    if success: 
        embed.set_image(url="https://jcboysha.com/STA/Green-alert.gif")
    if success and complications:
        embed.set_image(url="https://jcboysha.com/STA/Yellow-alert.gif")
    if not success: 
        embed.set_image(url="https://jcboysha.com/STA/Red-alert.gif")

    await ctx.send(embed=embed)

@bot.command(name="Scores", help="Get the Trivia high scores")
async def trivia(ctx):
    with open(SCORES) as scores:
        scoreset = json.load(scores)
        player = ctx.message.author.name
        await ctx.send("Your High Score is: " + str(scoreset[player]["High Score"]))

@bot.command(name="Trivia", help="Asks a Trivia Question. You have 15 seconds to answer!")
async def trivia(ctx):
    pscore = 0
    phighscore = 0
    player = ctx.message.author.name
    scoreset = {}

    response = "Answer the Question in 15 seconds!"
    await ctx.message.channel.send(response)

    with open(TRIVIA, encoding="utf-8") as questions:
        reader = csv.reader(questions) 
        chosen_row = random.choice(list(reader))
        answers = []
        for i in range(1,5):
            answers.append(chosen_row[i])
        await ctx.message.channel.send(chosen_row[0])
        choices = random.sample(answers, k=4)
        await ctx.message.channel.send ("1: " + choices[0] + "\n2: " + choices[1] + "\n3: " + choices[2] + "\n4: " + choices[3])

        def check(m):
            return m.content.isdigit() and m.author == ctx.author
        
    with open(SCORES) as scores:
        scoreset = json.load(scores)
        if player in scoreset:
            pscore = scoreset[player]["Score"]
            phighscore = scoreset[player]["High Score"]
        else:
            scoreset[player] = {}
            scoreset[player]["Score"] = 0
            scoreset[player]["High Score"] = 0

    try:
        guess = await bot.wait_for('message', check=check, timeout=15.0)

    except asyncio.TimeoutError:
        if pscore > phighscore:
            phighscore = pscore
        pscore = 0
        return await ctx.message.channel.send('Sorry, you took too long the answer was {}. \n Your high score is: ' + str(phighscore) + '' .format(answers[0]))

    if choices[int(guess.content)-1] == answers[0]:
        pscore += 1
        if pscore > phighscore:
            phighscore = pscore
        await ctx.message.channel.send('You are right! Your current score is: ' + str(pscore) + '\n Your high score is: ' + str(phighscore))
    else:
        if pscore > phighscore:
            phighscore = pscore
        pscore = 0
        await ctx.message.channel.send('Oh no! The answer was {}.'.format(answers[0]) + '\n Your high score is: ' + str(phighscore))
    
    scoreset[player]["Score"] = pscore
    scoreset[player]["High Score"] = phighscore

    with open(SCORES, "w") as scores:
        json.dump(scoreset, scores)

@bot.event
async def on_message(message):

    await bot.process_commands(message)

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name="get_char", help="View current player Stats.", category="STA")
async def getStat(ctx):
    await player_embed(ctx)

@bot.command(name="set_stats", help="sets various player stats.")
async def setStat(ctx, stat: str, op: str, value: int):
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

    await player_embed(ctx)

@bot.command(name="create_player", help="Creates a Player and Stats.  <more> \n\
usage: create_player <name> <race> <control> <daring> <fitness> \
<insight> <presence> <reason> <command> <conn> <security> <engineering> \
<science> <medicine>")
async def create_player(ctx, name: str, race: str, control: int,
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
        
    await player_embed(ctx)

bot.run(TOKEN)
