# RT - Test

from discord.ext import commands

from rtlib import Cog, RT


class Test(Cog):
    def __init__(self, bot: RT):
        self.bot = bot

    @commands.group()
    async def test(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.reply(self.ERRORS["WRONG_WAY"](ctx))

    @test.command()
    async def log(self, ctx: commands.Context, *, text: str):
        self.bot.dispatch("on_test_log", Cog.EventContext(ctx.guild, "SUCCESS", text))
        await ctx.reply("Ok")


async def setup(bot):
    await bot.add_cog(Test(bot))