from discord.ext import commands


class Cog:
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # type: commands.Bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Responds with "pong"."""
        await ctx.send('pong')

    # @commands.command(name='coolbot')
    # async def cool_bot(self, ctx):
    #     """Is the bot cool?"""
    #     await ctx.send('This bot is cool. :)')
    #
    # @commands.command(name='top_role', aliases=['toprole'])
    # @commands.guild_only()
    # async def show_toprole(self, ctx, *, member: discord.Member = None):
    #     """Simple command which shows the members Top Role."""
    #
    #     if member is None:
    #         member = ctx.author
    #
    #     await ctx.send(
    #         f'The top role for {member.display_name} is {member.top_role.name}')
    #
    # @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    # @commands.guild_only()
    # async def check_permissions(self, ctx, *, member: discord.Member = None):
    #     """A simple command which checks a members Guild Permissions.
    #     If member is not provided, the author will be checked."""
    #
    #     if not member:
    #         member = ctx.author
    #
    #     # Here we check if the value of each permission is True.
    #     perms = '\n'.join(
    #         perm for perm, value in member.guild_permissions if value)
    #
    #     # And to make it look nice, we wrap it in an Embed.
    #     embed = discord.Embed(title='Permissions for:',
    #                           description=ctx.guild.name, colour=member.colour)
    #     embed.set_author(icon_url=member.avatar_url, name=str(member))
    #
    #     # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
    #     embed.add_field(name='\uFEFF', value=perms)
    #
    #     await ctx.send(content=None, embed=embed)
    #     # Thanks to Gio for the Command.
