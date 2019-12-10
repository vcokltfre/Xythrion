#!/usr/bin/python3

"""
>> Xythrion
> Copyright (c) 2019 Xithrius
> MIT license, Refer to LICENSE for more info

This is the main Python file for the discord.py bot.
important attributes, checks, and background tasks are created here.

Running the bot:
    First time usage:
        $ py -3 -m pip install --user -r requirements.txt
    Starting the bot:
        $ py -3 bot.py

Todo:
    * Make bot available for everyone
    * https://github.com/3b1b/manim for animations
    * Image stuff
"""


import json
import collections
import asyncio
import datetime
import asyncpg
import aiohttp
import traceback
import sys

from discord.ext import commands as comms
import discord

from modules.output import path, cs, get_extensions


class Xythrion(comms.Bot):
    """Creating connections, attributes, and background tasks.

    Preface: When ctx is the context for the event, such as channel or member.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cs.w('Starting up...')
        #: Opening the config json file
        with open(path('config', 'config.json'), 'r', encoding='utf8') as f:
            data = json.load(f)
            cfg_data = json.dumps(data)

        #: Giving self.config recursive attributes from config.json
        self.config = json.loads(cfg_data, object_hook=lambda d:
                                 collections.namedtuple('config',
                                                        d.keys())(*d.values()))

        #: Create async loop
        self.loop = asyncio.get_event_loop()

        future = asyncio.gather()

        #: Create tasks
        self.loop.create_task(self.create_tasks())

        #: Run tasks
        self.loop.run_until_complete(future)

        #: Adding the main cog
        self.add_cog(Main_Cog(self))

    """ Subclass-specific tasks """

    async def create_tasks(self):
        """Session and database connections while testing service status.

        Raises:
            Errors depending on connection success/fail

        """
        await self.check_database()

        self.s = aiohttp.ClientSession()
        # cs.r('Session established successfully.')

        self.db_connection = asyncio.get_running_loop()
        await self.db_connection.create_task(self.check_database())

    async def check_database(self):
        with open(path('config', 'config.json'), 'r') as f:
            data = json.load(f)['db']

            #: Connecting to the database with config.json data.
            self.pool = await asyncpg.create_pool(**data, command_timeout=60)

        async with self.pool.acquire() as conn:
            await conn.execute('''CREATE TABLE IF NOT EXISTS Runtime(
                                    id serial PRIMARY KEY,
                                    login TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    logout TIMESTAMP WITHOUT TIME ZONE NOT NULL
                                    )''')
            await conn.execute('''CREATE TABLE IF NOT EXISTS Messages(
                                    id serial PRIMARY KEY,
                                    identification BIGINT,
                                    messages INTEGER)''')
            await conn.execute('''CREATE TABLE IF NOT EXISTS Users(
                                    id serial PRIMARY KEY,
                                    identification BIGINT,
                                    punishment_level INTEGER)''')

    """ Events """

    async def on_ready(self):
        """Bot event is triggered once login is successful.

        Returns:
            Success or failure message(s)

        Raises:
            An exception as e if something went wrong while loading extensions.

        """
        self.login_time = datetime.datetime.now()
        # cs.w('Loading extensions...')
        for extension in get_extensions():
            try:
                self.load_extension(extension)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__,
                                          file=sys.stderr)
        await self.change_presence(status=discord.ActivityType.playing,
                                   activity=discord.Game('with data'))
        cs.r('Startup completed.')

    async def close(self):
        """ Safely closes connections

        Args:
            None

        Raises:
            Some error items cannot be closed properly.

        Returns:
            Nothing since they're all passed.

        """
        try:
            await self.pool.close()
            await self.s.close()
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__,
                                      file=sys.stderr)
        await super().close()


class Main_Cog(comms.Cog):
    """Cog needed for essential commands"""

    def __init__(self, bot):
        self.bot = bot

    """ Checks """

    async def cog_check(self, ctx):
        """Checks if the command caller is an owner.

        Returns:
            True or false, depending on if the user is an owner.

        """
        return await self.bot.is_owner(ctx.author)

    """ Commands """

    @comms.command(aliases=['refresh', 'r'])
    async def reload(self, ctx):
        """Finds all cogs within the 'cogs' directory then loads/unloads them.

        Returns:
            Success or faliure message depending on extension loading

        """
        for ext in get_extensions():
            try:
                self.bot.unload_extension(ext)
                self.bot.load_extension(ext)
            except discord.ext.commands.ExtensionNotLoaded:
                self.bot.load_extension(ext)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__,
                                          file=sys.stderr)
        await ctx.send('Reloaded extensions.', delete_after=5)

    @comms.command(aliases=['disconnect', 'dc'])
    async def exit(self, ctx):
        """Logs out the bot.

        Returns:
            A possible timeout error.

        """
        logout_time = datetime.datetime.now()
        async with self.bot.pool.acquire() as conn:
            await conn.execute('''INSERT INTO Runtime(
                               login, logout) VALUES($1, $2)''',
                               self.bot.login_time, logout_time)
        cs.w('Logging out...')
        await ctx.bot.logout()


if __name__ == "__main__":

    #: Running the bot
    bot = Xythrion(command_prefix=comms.when_mentioned_or(';'),
                   case_insensitive=True)
    bot.run(bot.config.discord, bot=True, reconnect=True)
