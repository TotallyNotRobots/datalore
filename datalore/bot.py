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
import logging
import logging.config
import os
from pathlib import Path

from discord import Intents
from discord.ext import commands
from discord.ext.commands import Context

from datalore import db


def configure_loggers() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.captureWarnings(True)

    logger_names = ["datalore", "extensions", "discord", "asyncio"]

    dict_config = {
        "version": 1,
        "formatters": {
            "brief": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "full": {
                "format": "[%(asctime)s] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d][%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1000000,
                "backupCount": 5,
                "formatter": "full",
                "level": "INFO",
                "encoding": "utf-8",
                "filename": (log_dir / "bot.log"),
            },
        },
        "loggers": {
            name: {"level": "DEBUG", "handlers": ["console", "file"]}
            for name in logger_names
        },
    }

    logging.config.dictConfig(dict_config)


configure_loggers()

log = logging.getLogger(__name__)

intents = Intents.default()
intents.members = True

client = commands.Bot(
    command_prefix=os.getenv("COMMAND_PREFIX", "!"),
    case_insensitive=True,
    intents=intents,
)


@client.command("load")
async def load_cb(ctx: Context, extension: str) -> None:
    client.load_extension(f"extensions.{extension}")


@client.command("unload")
async def unload_cb(ctx: Context, extension: str) -> None:
    client.unload_extension(f"extensions.{extension}")


def load_extensions() -> None:
    for filename in os.listdir("extensions"):
        if filename.endswith(".py") and not filename.startswith("__"):
            client.load_extension(f"extensions.{filename[:-3]}")
            db.metadata.create_all(bind=db.engine)


def run_bot() -> None:
    client.run(os.environ["DISCORD_TOKEN"])


def main() -> None:
    log.info("Loading extensions...")
    load_extensions()
    log.info("Extensions loaded.")
    log.info("Starting bot...")
    run_bot()


if __name__ == "__main__":
    main()
