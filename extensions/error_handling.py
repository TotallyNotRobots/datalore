import logging

import discord
from discord.ext.typed_commands import (
    BadArgument,
    Bot,
    Cog,
    CommandNotFound,
    Context,
    DisabledCommand,
    NoPrivateMessage,
)

log = logging.getLogger(__name__)


class CommandErrorHandler(Cog[Context]):
    def __init__(self, bot: Bot[Context]) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        """The event triggered when an error is raised while invoking a command."""

        # This prevents any commands with local handlers being
        # handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return

        ignored = (CommandNotFound,)

        # Allows us to check for original exceptions raised and sent
        # to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")
        elif isinstance(error, NoPrivateMessage):
            try:
                await ctx.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass
        elif isinstance(error, BadArgument):
            await ctx.send("Bad arguments")
        else:
            # All other Errors not returned come here.
            # And we can just print the default TraceBack.
            log.exception(
                "Ignoring exception in command %s:", ctx.command, exc_info=error
            )


def setup(bot: Bot[Context]) -> None:
    bot.add_cog(CommandErrorHandler(bot))
