"""
> Xythrion
> Copyright (c) 2020 Xithrius
> MIT license, Refer to LICENSE for more info
"""


import sys
import traceback

from discord.ext import commands as comms


class Warnings(comms.Cog):
    """Warning the user about specific actions taken.

    Attributes:
        bot (:obj:`comms.Bot`): Represents a Discord bot.

    """

    def __init__(self, bot):
        """Creating important attributes for this class.

        Args:
            bot (:obj:`comms.Bot`): Represents a Discord bot.

        """
        self.bot = bot

    """ Events """

    @comms.Cog.listener()
    async def on_command_completion(self, ctx):
        """Adds a reaction after a command is successfully completed.

        Args:
            ctx (comms.Context): Represents the context in which a command is being invoked under.

        """
        await ctx.message.add_reaction('\U00002705')

    @comms.Cog.listener()
    async def on_command_error(self, ctx, error):
        """When the command has an error, this event is triggered.

        Args:
            ctx (comms.Context): Represents the context in which a command is being invoked under.
            error (comms.CommandError): The error that was raised

        """
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        await ctx.message.add_reaction('\U0000274c')

        if isinstance(error, comms.DisabledCommand):
            return await ctx.send(f'`Command not available.`')

        elif isinstance(error, comms.CommandNotFound):
            return await ctx.send(f'`Command not found.`')

        elif isinstance(error, comms.UserInputError):
            return await ctx.send(f'`Command raised bad argument: {error}`')

        elif isinstance(error, comms.NotOwner):
            return await ctx.send('`You do not have enough permissions for this command.`')

        elif isinstance(error, comms.CommandOnCooldown):
            return await ctx.send(f'`{error}`')

        elif isinstance(error, comms.CheckFailure):
            if str(error).strip() == 'NSFW':
                return await ctx.send('`NSFW in SFW channels are not allowed.`')
            return await ctx.send(f'`You do not have enough permissions to run this command.`')

        elif isinstance(error, AssertionError):
            return await ctx.send(f'`Command failed: {error}`')

        else:
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Warnings(bot))
