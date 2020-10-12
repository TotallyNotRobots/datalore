from typing import Optional

from discord import Guild, Member


def find_user_in_guild(guild: Guild, user_name: str) -> Optional[Member]:
    for member in guild.members:
        if member.display_name.lower() == user_name.lower():
            return member

    return None
