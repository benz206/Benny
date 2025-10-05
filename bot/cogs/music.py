import discord
import mafic
from discord.ext import commands


class Music(commands.Cog):
    """
    Mafic-based music commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.pool: mafic.NodePool | None = None

    async def connect_nodes(self) -> None:
        if not getattr(self.bot, "MUSIC_ENABLED", True):
            return
        if self.pool is None:
            self.pool = mafic.NodePool(self.bot)
        await self.pool.create_node(
            host="127.0.0.1",
            port=2333,
            label="MAIN",
            password="BennyBotRoot",
        )

    @commands.Cog.listener()
    async def on_connect_mafic(self) -> None:
        await self.connect_nodes()

    async def ensure_player(self, ctx: commands.Context) -> mafic.Player:
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.BadArgument("You must be connected to a voice channel.")
        if ctx.voice_client:
            return ctx.voice_client  # type: ignore[return-value]
        return await ctx.author.voice.channel.connect(cls=mafic.Player)  # type: ignore[arg-type]

    @commands.hybrid_command(name="play", aliases=["p"], description="Play a track")
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def play_cmd(self, ctx: commands.Context, *, query: str) -> None:
        player = await self.ensure_player(ctx)
        tracks = await player.fetch_tracks(query)
        if not tracks:
            raise commands.BadArgument("No tracks found.")
        await player.play(tracks[0])
        await ctx.reply(f"Playing {tracks[0].title}.")

    @commands.hybrid_command(
        name="disconnect", aliases=["dc"], description="Disconnect the bot"
    )
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def dc_cmd(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            raise commands.BadArgument("I'm not connected to voice.")
        await ctx.voice_client.disconnect(force=True)
        await ctx.reply("Disconnected.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
