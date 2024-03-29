# RT - General

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic, ParamSpec, Optional, Any

from discord.ext import commands
from discord.ext.fslash import is_fslash
import discord

from rtutil.utils import _set_t

from rtlib.common.utils import make_error_message, code_block, text_format
from rtlib.common import reply_error

from .utils import gettext
from .types_ import NameIdObj, MentionIdObj
from .bot import RT
from . import tdpocket

from data import Colors

if TYPE_CHECKING:
    from .rtevent import EventContext
    from .help import Help, HelpCommand, Text


__all__ = ("RT", "Cog", "t", "cast", "Embed")


class Embed(discord.Embed):
    "Botのテーマカラーをデフォルトで設定するようにした`Embed`です。"

    def __init__(self, title: str, *args, **kwargs):
        kwargs["title"] = title
        kwargs.setdefault("color", Colors.normal)
        super().__init__(*args, **kwargs)


def _get_client(obj):
    return obj._state._get_client()


def t(text: Text, ctx: Any, ignore_key_error: bool = False, **kwargs) -> str:
    """Extracts strings in the correct language from a dictionary of language code keys and their corresponding strings, based on information such as the `ctx` guild passed in.
    You can use keyword arguments to exchange strings like f-string."""
    # Extract client
    client: Optional[RT] = kwargs.pop("client", None)
    user, gu = False, False
    if isinstance(ctx, (discord.User, discord.Member, discord.Object)):
        client = _get_client(ctx) # type: ignore
        user = True
    elif getattr(ctx, "message", None) and not is_fslash(ctx):
        client = _get_client(ctx.message)
    elif getattr(ctx, "guild", None):
        client = _get_client(ctx.guild)
    elif getattr(ctx, "channel", None):
        client = _get_client(ctx.channel)
    elif getattr(ctx, "user", None):
        client = _get_client(ctx.user)
    elif gu := isinstance(ctx, (discord.Guild, discord.User)):
        client = _get_client(ctx) # type: ignore
    # Extract correct text
    if client is None:
        text = gettext(text, "en") # type: ignore
    elif isinstance(ctx, int):
        text = gettext(text, client.language.user.get(ctx) # type: ignore
            or client.language.guild.get(ctx))
    else:
        language = None
        if user:
            language = client.language.user.get(ctx.id)
        else:
            if getattr(ctx, "user", None):
                language = client.language.user.get(ctx.user.id) # type: ignore
            if language is None and getattr(ctx, "author", None):
                language = client.language.user.get(ctx.author.id) # type: ignore
            if language is None and getattr(ctx, "guild", None):
                language = client.language.guild.get(ctx.guild.id) # type: ignore
            if language is None and gu:
                language = client.language.guild.get(ctx.id)
            if language is None: language = "en"
        text = gettext(text, "en") if language is None else gettext(text, language) # type: ignore
    try:
        return text.format(**kwargs) # type: ignore
    except KeyError:
        if ignore_key_error:
            return text # type: ignore
        else:
            raise
tdpocket.t = t
_set_t(t)


UCReT = TypeVar("UCReT")
PoP = ParamSpec("PoP")
PoT = TypeVar("PoT")
CogT = TypeVar("CogT")
class Cog(commands.Cog):
    "Extended cog"

    class Context(commands.Context, Generic[CogT]):
        cog: CogT
        guild: discord.Guild
        author: discord.Member
        channel: discord.TextChannel | discord.ForumChannel | discord.VoiceChannel | discord.Thread

    text_format = staticmethod(text_format)
    detail_or = staticmethod(lambda detail: "ERROR" if detail else "SUCCESS")
    reply_error = reply_error
    Help: type[Help]
    HelpCommand: type[HelpCommand]
    Embed = Embed
    ERRORS = {
        "WRONG_WAY": lambda ctx: t(dict(
            ja="使い方が違います。", en="This is wrong way to use this command."
        ), ctx)
    }
    t = staticmethod(t)
    EventContext: type[EventContext]
    bot: RT

    async def group_index(self, ctx: commands.Context) -> None:
        "グループコマンドが実行された際に「使用方法が違います」と返信します。"
        if not ctx.invoked_subcommand:
            await ctx.reply(t({
                "ja": "使用方法が違います。", "en": "It is wrong way to use this command."
            }, ctx))

    @staticmethod
    def mention_and_id(obj: MentionIdObj) -> str:
        return f"{obj.mention} (`{obj.id}`)"

    @staticmethod
    def name_and_id(obj: NameIdObj) -> str:
        return f"{obj.name} (`{obj.id}`)"

    def embed(self, **kwargs) -> Embed:
        "Make embed and set title to the cog name."
        return Embed(self.__cog_name__, **kwargs)

    CONSTANT_FOR_EXCEPTION_TO_TEXT = {
        "ja": "内部エラーが発生しました。", "en": "An internal error has occurred."
    }

    @staticmethod
    def error_to_text(error: Exception) -> Text:
        error = code_block(make_error_message(error), "python") # type: ignore
        return {
            key: f"{Cog.CONSTANT_FOR_EXCEPTION_TO_TEXT[key]}\n{error}"
            for key in ("ja", "en")
        }


def cast(**kwargs: dict[str, str]) -> str:
    return kwargs # type: ignore