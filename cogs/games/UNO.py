"""
> Xythrion
> Copyright (c) 2020 Xithrius
> MIT license, Refer to LICENSE for more info
"""


from discord.ext import commands as comms


class UNO(comms.Cog):
    """Summary for UNO

    Attributes:
        bot (:obj:`comms.Bot`): Represents a Discord bot.

    """

    def __init__(self, bot):
        """Creating important attributes for this class.

        Args:
            bot (:obj:`comms.Bot`): Represents a Discord bot.

        """
        self.bot = bot

    """ Commands """

    @comms.command(enabled=False)
    async def uno(self, ctx):
        """Plays a move in uno

        Args:
            ctx (:obj:`comms.Context`): Represents the context in which a command is being invoked under.

        Command examples:
            >>> [prefix]uno play card

        """
        await ctx.send(
            '`Feature will be implimented be in later versions, I promise (Unless it is impossible).`'
        )


def setup(bot):
    bot.add_cog(UNO(bot))
