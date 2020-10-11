"""
Trivia - A COG Module for the Datalore Discord bot
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
import asyncio
import json
import os
import random
from pathlib import Path
from typing import List, cast

from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from ruamel.yaml import YAML, yaml_object
from sqlalchemy import Column, Integer, String

from datalore import db


# noinspection PyUnusedName
class PlayerScore(db.Base):
    __tablename__ = "trivia_scores"

    player = Column(String(), primary_key=True, index=True)

    score = Column(Integer(), default=0)
    high_score = Column(Integer(), default=0)

    @classmethod
    def get(cls, user: str) -> "PlayerScore":
        session = db.Session()
        state = cast(PlayerScore, session.query(cls).get(user))
        if state is None:
            state = PlayerScore(player=user)
            session.add(state)
            session.commit()

        return state


yaml = YAML()


@yaml_object(yaml)
class Question:
    yaml_tag = "!question"

    def __init__(self, question: str, answer: str, options: List[str]) -> None:
        self.question = question
        self.answer = answer
        self.options = options

    def __repr__(self) -> str:
        return (
            f"Question(question={self.question!r}, "
            f"answer={self.answer!r}, options={self.options!r})"
        )


class Trivia(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.questions = self.load_data()

    @staticmethod
    def load_data() -> List[Question]:
        with open("data/trivia.yml", encoding="utf-8") as file:
            return cast(List[Question], yaml.load(file))

    @commands.command(name="scores", help="Get the Trivia high scores")
    async def scores(self, ctx: Context) -> None:
        await ctx.send(
            f"Your High Score is: {PlayerScore.get(ctx.author.name).high_score}"
        )

    @commands.command(
        name="trivia",
        help="Asks a Trivia Question. You have 30 seconds to answer!",
    )
    async def trivia(self, ctx: Context) -> None:
        player = ctx.message.author.name
        score = PlayerScore.get(player)

        response = "Answer the Question in 30 seconds!"
        await ctx.send(response)
        chosen_row = random.choice(self.questions)

        possible_answers = [chosen_row.answer] + random.sample(
            chosen_row.options, k=3
        )

        random.shuffle(possible_answers)

        await ctx.send(chosen_row.question)
        choices = random.sample(possible_answers, k=4)
        msg = "\n".join(f"{i+1}: {choice}" for i, choice in enumerate(choices))
        await ctx.send(msg)

        def check(match: Message) -> bool:
            return bool(match.content.isdigit() and match.author == ctx.author)

        try:
            guess = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            score.score = 0
            await ctx.send(
                f"Sorry, you took too long! The answer was {chosen_row.answer}.\n"
                f"Your high score is: {score.high_score}"
            )
            db.Session().commit()
            return

        if choices[int(guess.content) - 1] == chosen_row.answer:
            score.score += 1
            new_high_score = False
            if score.score > score.high_score:
                score.high_score = score.score
                new_high_score = True

            await ctx.message.channel.send(
                f"You are right! Your current score is: {score.score}\n"
                f"Your high score is: {score.high_score}"
            )
            if new_high_score:
                await ctx.send("New high score \N{party popper}")
        else:
            score.score = 0
            await ctx.message.channel.send(
                f'Oh no! The answer was: "{chosen_row.answer}".\n'
                f"Your high score is: {score.high_score}"
            )

        db.Session().commit()


def db_init() -> None:
    session = db.Session()
    scores_file_name = os.getenv("SCORES")

    PlayerScore.__table__.create(db.engine, True)
    if session.query(PlayerScore).count() <= 0 and scores_file_name:
        scores_file = Path(scores_file_name)
        if scores_file.exists():
            with open(scores_file, encoding="utf-8") as file:
                data = json.load(file)

            for player, score in data.items():
                session.add(
                    PlayerScore(
                        player=player,
                        score=int(score["Score"]),
                        high_score=int(score["High Score"]),
                    )
                )

    session.commit()


def setup(bot: Bot) -> None:
    db_init()
    bot.add_cog(Trivia(bot))
