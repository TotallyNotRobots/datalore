import os, discord, csv, random, asyncio, json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

SCORES = os.getenv('SCORES')
TRIVIA = os.getenv('TRIVIA')

class Trivia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Scores", help="Get the Trivia high scores")
    async def scores(self, ctx):
        with open(SCORES) as scores:
            scoreset = json.load(scores)
            player = ctx.message.author.name
            await ctx.send("Your High Score is: " + str(scoreset[player]["High Score"]))

    @commands.command(name="Trivia", help="Asks a Trivia Question. You have 15 seconds to answer!")
    async def trivia(self, ctx):
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
            guess = await self.bot.wait_for('message', check=check, timeout=15.0)

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

def setup(bot):
    bot.add_cog(Trivia(bot))