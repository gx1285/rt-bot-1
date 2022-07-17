# RT Music - Utils

from textwrap import shorten

import discord


def can_control(member: discord.Member, dj_role_id: int | None) -> bool:
    "音楽再生の操作をすることができるかどうかを返します。"
    assert member.voice is not None and member.voice.channel is not None
    return (dj_role_id is not None and member.get_role(dj_role_id) is not None) \
        or member.guild_permissions.administrator \
        or all(m.bot for m in member.voice.channel.members if m.id != member.id)


hundred_shorten = lambda text, *args, **kwargs: \
    shorten(text, 100, *args, **kwargs, placeholder="...")
"百文字で切ります。"