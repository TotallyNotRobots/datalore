"""
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
"""
import json
import os
import random
from pathlib import Path
from typing import Optional, cast

import discord
from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context
from sqlalchemy import Column, Integer, String

from datalore import db

img_dir = Path("imgs").resolve()


# noinspection PyUnusedName
class Character(db.Base):
    """
    Player's character data
    """

    __tablename__ = "characters"

    name = Column(String(), index=True)
    player = Column(String(), index=True, primary_key=True)
    race = Column(String())
    stress = Column(Integer(), default=0)
    determination = Column(Integer(), default=0)

    # Attributes
    attr_control = Column(Integer())
    attr_fitness = Column(Integer())
    attr_presence = Column(Integer())
    attr_daring = Column(Integer())
    attr_insight = Column(Integer())
    attr_reason = Column(Integer())

    # Disciplines
    disc_command = Column(Integer())
    disc_security = Column(Integer())
    disc_science = Column(Integer())
    disc_engineering = Column(Integer())
    disc_medicine = Column(Integer())
    disc_conn = Column(Integer())

    @classmethod
    def get(cls, player: str) -> "Character":
        """
        Get a player's character

        :param player: Player's name
        :return: Player's character or None
        """
        return cast(Character, db.Session().query(cls).get(player))

    def set_attribute(self, name: str, value: int) -> None:
        """
        Set an attribute
        :param name: Attribute name
        :param value: Value to set
        """
        setattr(self, f"attr_{name.lower()}", value)

    def get_attribute(self, name: str) -> int:
        """
        Get an attribute

        :param name: Attribute name
        :return: The attribute's value
        """
        return cast(int, getattr(self, f"attr_{name.lower()}"))

    def set_discipline(self, name: str, value: int) -> None:
        """
        Set a discipline value
        :param name: Discipline name
        :param value: Value to set
        """
        setattr(self, f"disc_{name.lower()}", value)

    def get_discipline(self, name: str) -> int:
        """
        Get a discipline value

        :param name: Discipline name
        :return: Discipline value
        """
        return cast(int, getattr(self, f"disc_{name.lower()}"))


# noinspection PyUnusedName
class GameState(db.Base):
    """
    Game state
    """

    __tablename__ = "game_state"

    channel = Column(String(), primary_key=True, index=True)

    momentum = Column(Integer())
    threat = Column(Integer())

    @classmethod
    def get(cls, channel: str) -> "GameState":
        """
        Get a game state

        :param channel: Channel to get the state for
        :return: Current state
        """
        session = db.Session()
        state = session.query(cls).get(channel)
        if state is None:
            state = GameState(channel=channel, momentum=0, threat=0)
            session.add(state)
            session.commit(state)

        return cast(GameState, state)

    def add_momentum(self, momentum: int) -> None:
        self.momentum = min(self.momentum + momentum, 6)

    def add_threat(self, threat: int) -> None:
        self.threat = min(self.threat + threat, 10)

    def sub_threat(self, diff: int = 1) -> bool:
        if self.threat < diff:
            return False

        self.threat -= diff
        return True

    def sub_momentum(self, diff: int = 1) -> bool:
        if self.momentum < diff:
            return False

        self.momentum -= diff
        return True


class ChallengeRoll:
    def __init__(
        self,
        has_complications: bool,
        succeeded: bool,
        embed: Embed,
        successes: int,
        complications: int,
    ) -> None:
        self.has_complications = has_complications
        self.embed = embed
        self.successes = successes
        self.complications = complications
        self.succeeded = succeeded

    def get_img(self) -> discord.File:
        if self.succeeded:
            if self.has_complications:
                file = get_img("Yellow-alert.gif")
            else:
                file = get_img("Green-alert.gif")
        else:
            file = get_img("Red-alert.gif")

        return file

    @classmethod
    def do_roll(
        cls,
        dice_count: int,
        challenge_value: int,
        focus: bool,
        discipline_value: int,
        attribute_value: int,
        discipline: str,
        attribute: str,
        difficulty: int,
    ) -> "ChallengeRoll":
        successes = 0
        complications = 0
        has_complications = False
        rolls = [random.randint(1, 20) for _ in range(dice_count)]

        for roll in rolls:
            if roll >= 20:
                complications += 1

            if roll <= challenge_value:
                successes += 1

            if roll == 1:
                successes += 1

            if focus:
                if roll < discipline_value:
                    complications += 1

        succeeded = successes >= difficulty
        if complications > 0:
            has_complications = True

        if succeeded:
            if has_complications:
                color = Colour.gold()
            else:
                color = Colour.green()
        else:
            color = Colour.red()

        embed = discord.Embed(
            title="Challenge",
            description=f"{discipline.title()} ({discipline_value}) "
            f"+ {attribute.title()} ({attribute_value})",
            colour=color,
        )

        embed.add_field(
            name="Difficulty: ", value=str(difficulty), inline=False
        )
        embed.add_field(name="Successes: ", value=str(successes))
        embed.add_field(name="Complications: ", value=str(complications))
        embed.add_field(name="Rolls: ", value=str(rolls))

        return cls(
            complications=complications,
            has_complications=has_complications,
            embed=embed,
            succeeded=succeeded,
            successes=successes,
        )


def get_img(name: str) -> discord.File:
    return discord.File(img_dir / name)


class STA(commands.Cog):
    """
    Plugin implementation
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    async def player_embed(ctx: Context, player: Optional[str] = None) -> None:
        """
        Display player info
        :param ctx: Context to show the data in
        :param player: Player to show, defaults to calling player
        """
        if player is None:
            player = str(ctx.author.name)

        character = Character.get(player)

        embed = discord.Embed(
            title=character.name,
            description=character.race,
            colour=discord.Colour.blue(),
        )

        file = get_img("Commbadge.png")

        embed.set_author(name=player, icon_url=f"attachment://{file.filename}")

        embed.add_field(name="Stress", value=str(character.stress))
        embed.add_field(
            name="Determination", value=str(character.determination)
        )
        embed.add_field(name="Attributes", value="---", inline=False)
        embed.add_field(name="Control", value=str(character.attr_control))
        embed.add_field(name="Fitness", value=str(character.attr_fitness))
        embed.add_field(name="Presence", value=str(character.attr_presence))
        embed.add_field(name="Daring", value=str(character.attr_daring))
        embed.add_field(name="Insight", value=str(character.attr_insight))
        embed.add_field(name="Reason", value=str(character.attr_reason))
        embed.add_field(name="Disciplines", value="---", inline=False)
        embed.add_field(name="Command", value=str(character.disc_command))
        embed.add_field(name="Security", value=str(character.disc_security))
        embed.add_field(name="Science", value=str(character.disc_science))
        embed.add_field(name="Conn", value=str(character.disc_conn))
        embed.add_field(
            name="Engineering", value=str(character.disc_engineering)
        )
        embed.add_field(name="Medicine", value=str(character.disc_medicine))

        await ctx.send(embed=embed, file=file)

    @commands.command(name="dmg", help="Roll Damage.")
    async def damage(self, ctx: Context, dice_pool: int) -> None:
        """
        Roll a damage check
        :param ctx: Command context
        :param dice_pool: Number of dice to roll
        """
        rolls = []
        dmg = 0
        effects = 0
        for _ in range(0, dice_pool):
            rolls.append(random.randint(1, 6))

        for roll in rolls:
            if roll == 1:
                dmg += 1
            elif roll == 2:
                dmg += 2
            elif roll == 5:
                dmg += 1
                effects += 1
            elif roll == 6:
                dmg += 1
                effects += 1

        embed = discord.Embed(
            title="Damage Result", colour=discord.Colour.magenta()
        )

        embed.add_field(name="Damage: ", value=str(dmg))
        embed.add_field(name="Effects: ", value=str(effects))
        embed.add_field(name="Rolls: ", value=str(rolls), inline=False)

        await ctx.send(embed=embed)

    @staticmethod
    async def show_game(ctx: Context, state: GameState, color: Colour) -> None:
        """
        Display game info

        :param ctx: Context to show game info in
        :param state: GameState to show
        :param color: Color to use
        """
        embed = discord.Embed(
            title="Game Stats",
            description=f"***{state.channel}***  Threat and Momentum",
            colour=color,
        )

        embed.add_field(name="Momentum", value=str(state.momentum))
        embed.add_field(name="Threat", value=str(state.threat))

        await ctx.send(embed=embed)

    async def set_game_stat(
        self, ctx: Context, stat: str, diff: int, send: bool = True
    ) -> None:
        """
        Set a stat on the game state

        :param ctx: Game context
        :param stat: Stat name
        :param diff: Stat change
        :param send: Whether to send the changed values
        """
        channel = ctx.channel.name
        state = GameState.get(channel)
        try:
            value = getattr(state, stat.lower())
            setattr(state, stat.lower(), value + diff)
        except AttributeError:
            await ctx.send(f"Bad stat: {stat}")
            return

        if send:
            await self.show_game(ctx, state, color=discord.Colour.magenta())

        db.Session().commit()

    @commands.group(
        name="game_stats",
        aliases=["gamestats", "gstats", "game"],
        help="View and Modify current Game Stats",
    )
    async def game_stats(
        self,
        ctx: Context,
    ) -> None:
        channel = ctx.channel.name
        state = GameState.get(channel)

        if ctx.invoked_subcommand is None:
            await self.show_game(ctx, state, Colour.gold())
            return

    @game_stats.command(name="add")
    async def add_game(self, ctx: Context, stat: str, value: int) -> None:
        await self.set_game_stat(ctx, stat, value)
        db.Session().commit()

    @game_stats.command(name="sub")
    async def sub_game(self, ctx: Context, stat: str, value: int) -> None:
        await self.set_game_stat(ctx, stat, -value)
        db.Session().commit()

    @commands.command(
        name="get_char",
        aliases=["getchar", "char"],
        help="View current player Stats.",
    )
    async def get_stat(self, ctx: Context) -> None:
        await self.player_embed(ctx)

    @commands.command(name="set_stats", help="sets various player stats.")
    async def set_stat(
        self, ctx: Context, stat: str, subcmd: str, value: int
    ) -> None:
        player = ctx.author.name
        character = Character.get(player)

        stat_lower = stat.lower()
        if subcmd == "set":
            if stat_lower in ["det", "determination"]:
                character.determination = value
            elif stat_lower in ["stress", "str"]:
                character.stress = value
        else:
            if subcmd == "add":
                change = value
            elif subcmd == "sub":
                change = -value
            else:
                await ctx.send(f"Bad operation: {subcmd}")
                return

            if stat_lower in ["det", "determination"]:
                character.determination += change
            elif stat_lower in ["stress", "str"]:
                character.stress += change

        db.Session().commit()
        await self.player_embed(ctx)

    @commands.command(name="set_attr", help="sets player attribute to value.")
    async def set_attr(self, ctx: Context, stat: str, value: int) -> None:
        player = ctx.author.name
        character = Character.get(player)
        try:
            character.set_attribute(stat, value)
        except AttributeError:
            await ctx.send(f"Unknown attribute: {stat}")
            return

        db.Session().commit()

        await self.player_embed(ctx)

    @commands.command(name="set_disc", help="sets player discipline to value.")
    async def set_disc(self, ctx: Context, disc: str, value: int) -> None:
        character = Character.get(ctx.message.author.name)
        try:
            character.set_discipline(disc, value)
        except AttributeError:
            await ctx.send(f"Unknown discipline: {disc}")
            return

        db.Session().commit()
        await self.player_embed(ctx)

    @commands.command(
        name="create_player",
        help="Creates a Player and Stats.",
    )
    async def create_player(
        self,
        ctx: Context,
        name: str,
        race: str,
        control: int,
        daring: int,
        fitness: int,
        insight: int,
        presence: int,
        reason: int,
        command: int,
        conn: int,
        security: int,
        engineering: int,
        science: int,
        medicine: int,
    ) -> None:
        player: str = ctx.author.name
        character = Character.get(player)

        if character:
            await ctx.send(
                f"{player} already has a Character ({character.name})."
            )
            return

        character = Character(
            name=name,
            race=race,
            attr_control=control,
            attr_fitness=fitness,
            attr_daring=daring,
            attr_insight=insight,
            attr_presence=presence,
            attr_reason=reason,
            disc_conn=conn,
            disc_command=command,
            disc_medicine=medicine,
            disc_science=science,
            disc_security=security,
            disc_engineering=engineering,
            player=player,
        )
        session = db.Session()
        session.add(character)
        session.commit()
        await ctx.send("Character created!")

        await self.player_embed(ctx)

    @commands.command(
        name="challenge",
        help="Undertake a challenge.",
    )
    async def challenge(
        self,
        ctx: Context,
        attribute: str,
        discipline: str,
        difficulty: int,
        num_dice: int,
        focus: bool = False,
    ) -> None:
        player: str = ctx.author.name
        character = Character.get(player)

        try:
            attr = character.get_attribute(attribute)
        except AttributeError:
            await ctx.send(f"Bad attribute: {attribute}")
            return

        try:
            disc = character.get_discipline(discipline)
        except AttributeError:
            await ctx.send(f"Bad discipline: {discipline}")
            return

        challenge_value = attr + disc

        # Success, Complication
        roll = ChallengeRoll.do_roll(
            num_dice,
            challenge_value,
            focus,
            disc,
            attr,
            discipline,
            attribute,
            difficulty,
        )
        embed = roll.embed
        if roll.successes > difficulty:
            momentum = roll.successes - difficulty
            embed.add_field(name="Momentum: ", value=f"+{momentum}")
            GameState.get(ctx.channel).add_momentum(momentum)

        file = roll.get_img()

        embed.set_image(url=f"attachment://{file.filename}")

        await ctx.send(embed=embed, file=file)

    @commands.command(
        name="gm_challenge",
        aliases=["gmchallenge"],
        help="Undertake a challenge.",
    )
    async def gm_challenge(
        self,
        ctx: Context,
        attribute: str,
        attribute_value: int,
        discipline: str,
        discipline_value: int,
        difficulty: int,
        num_dict: int,
        focus: bool = False,
    ) -> None:
        challenge_value = attribute_value + discipline_value

        roll = ChallengeRoll.do_roll(
            num_dict,
            challenge_value,
            focus,
            discipline_value,
            attribute_value,
            discipline,
            attribute,
            difficulty,
        )

        embed = roll.embed

        if roll.successes > difficulty:
            threat = roll.successes - difficulty
            embed.add_field(name="Threat: ", value=str(threat))
            GameState.get(ctx.channel.name).add_threat(threat)

        db.Session().commit()

        file = roll.get_img()

        embed.set_image(url=f"attachment://{file.filename}")

        await ctx.send(embed=embed, file=file)


def init_db() -> None:
    """
    Migrate game data if it is still in the old format
    """
    session = db.Session()
    stats_file_name = os.getenv("STA_STATS")
    game_stats_file_prefix = os.getenv("GAME_STATS")
    Character.__table__.create(db.engine, True)
    if session.query(Character).count() <= 0 and stats_file_name:
        stats_file = Path(stats_file_name)
        if stats_file.exists():
            with open(stats_file, encoding="utf-8") as file:
                data = json.load(file)

            for player, char in data.items():
                attributes = {
                    f"attr_{k.lower()}": int(v)
                    for k, v in char["Attributes"].items()
                }

                disciplines = {
                    f"disc_{k.lower()}": int(v)
                    for k, v in char["Disciplines"].items()
                }

                character = Character(
                    player=player,
                    name=char["Name"],
                    race=char["Race"],
                    stress=int(char["Stress"]),
                    determination=int(char["Determination"]),
                    **attributes,
                    **disciplines,
                )

                session.add(character)

    GameState.__table__.create(db.engine, True)
    if session.query(GameState).count() <= 0 and game_stats_file_prefix:
        game_stats_file = Path(game_stats_file_prefix)
        game_stats_files = list(
            game_stats_file.parent.rglob(f"{game_stats_file.name}*.json")
        )

        for path in game_stats_files:
            channel = path.name.rsplit(".")[-2]

            with open(path, encoding="utf-8") as file:
                data = json.load(file)

            session.add(
                GameState(
                    channel=channel,
                    momentum=int(data["Momentum"]),
                    threat=int(data["Stress"]),
                )
            )

    session.commit()


def setup(bot: Bot) -> None:
    """
    Setup the plugin

    :param bot: Bot to add the plugin to
    """
    init_db()
    bot.add_cog(STA(bot))
