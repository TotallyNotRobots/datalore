import asyncio
import random
from asyncio import Future
from typing import Iterable, List, cast
from unittest.mock import MagicMock, call

import pytest
from discord import Embed, File
from discord.embeds import EmbedProxy
from sqlalchemy import create_engine

from datalore import db
from extensions.sta import STA, Character


@pytest.fixture(name="set_db")
def set_db_fixture() -> Iterable[None]:
    bind = create_engine("sqlite:///:memory:")
    try:
        db.Session.configure(bind=bind)  # type: ignore
        db.metadata.bind = bind
        db.engine = bind
        db.metadata.create_all()
        yield
    finally:
        db.Session.remove()  # type: ignore
        db.Session.configure(bind=None)  # type: ignore
        db.metadata.bind = None
        db.engine = None


class AssertEmbed:
    def __init__(self, actual: EmbedProxy) -> None:
        self.actual = actual

    def has_name(self, name: str) -> "AssertEmbed":
        assert cast(str, self.actual.name) == name
        return self

    def has_value(self, value: str) -> "AssertEmbed":
        assert cast(str, self.actual.value) == value
        return self


@pytest.mark.asyncio()
@pytest.mark.usefixtures("set_db")
async def test_del_char() -> None:
    session = db.Session()
    guild_id = 555
    player_id = 111
    session.add(
        Character(
            guild=guild_id,
            player=player_id,
            name="name",
            race="race",
            attr_reason=5,
            disc_science=12,
        )
    )
    session.commit()
    cog = STA()
    context = MagicMock()
    context.author.id = player_id
    context.guild.id = guild_id
    context.guild.__bool__.return_value = True
    context.author.__bool__.return_value = True
    future: Future[bool] = asyncio.Future()
    future.set_result(True)
    context.send.return_value = future
    context.mock_add_spec(["guild", "author", "send"], spec_set=True)

    assert db.Session().query(Character).count() == 1
    await STA.del_char(cog, context)
    assert db.Session().query(Character).count() == 0

    assert context.mock_calls == [
        call.guild.__bool__(),
        call.send("Character deleted."),
    ]


@pytest.mark.asyncio()
@pytest.mark.usefixtures("set_db")
async def test_challenge() -> None:
    random.seed(1)
    session = db.Session()
    guild_id = 555
    player_id = 111
    session.add(
        Character(
            guild=guild_id,
            player=player_id,
            name="name",
            race="race",
            attr_reason=5,
            disc_science=12,
        )
    )
    session.commit()
    cog = STA()
    context = MagicMock()
    context.author.id = player_id
    context.guild.id = guild_id
    future: Future[bool] = asyncio.Future()
    future.set_result(True)
    context.send.return_value = future
    context.mock_add_spec(["guild", "author", "send"], spec_set=True)
    res = await STA.challenge(cog, context, "REason", "science", 2, 2)
    assert res is None
    msg = context.send.mock_calls[0]
    embed: Embed = msg.kwargs["embed"]
    file: File = msg.kwargs["file"]

    # This is done by send normally
    file.close()

    assert embed.author.name == Embed.Empty
    assert embed.title == "Challenge"
    fields = cast(List[EmbedProxy], embed.fields)
    AssertEmbed(fields[0]).has_name("Difficulty: ").has_value("2")
    AssertEmbed(fields[1]).has_name("Successes: ").has_value("1")
    AssertEmbed(fields[2]).has_name("Complications: ").has_value("0")
    AssertEmbed(fields[3]).has_name("Rolls: ").has_value("[5, 19]")
    assert embed.image.url == "attachment://Red-alert.gif"
    assert file.filename == "Red-alert.gif"
