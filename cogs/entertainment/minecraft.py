# RT - Minecraft search

import discord
from discord.ext import commands
from core import RT, Cog
from rtutil.minecraft import search, NotFound

class MinecraftSearch(Cog):
    def __init__(self, bot: RT):
        self.bot = bot
        
    @commands.command()
    async def minecraft(self, user: str):
        try:
            result = await search(user)
        except NotFound:
            await ctx.send("I can't found that user")
        else:
            embed = discord.Embed(title=result.name)
            embed.add_field(name="UUID", value=result.id)
            embed.set_image(url=result.skin)
            await ctx.send(embed=embed)
            

async def setup(bot: RT):
    await bot.add_cog(MinecraftSearch(bot))
