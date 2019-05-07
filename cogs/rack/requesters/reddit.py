'''

+----[ Relay.py ]-------------------------------+
|                                               |
|  Copyright (c) 2019 Xithrius                  |
|  MIT license, Refer to LICENSE for more info  |
|                                               |
+-----------------------------------------------+

'''


# //////////////////////////////////////////////////////////////////////////// #
# Libraries                                                                    #
# //////////////////////////////////////////////////////////////////////////// #
# Built-in modules, third-party modules, custom modules                        #
# //////////////////////////////////////////////////////////////////////////// #


import asyncio
import json
import requests
import platform

from discord.ext import commands as comms
import discord

from relay.containers.output.printer import printc
from relay.containers.QOL.pathing import path
from relay.containers.QOL.shortened import now


# //////////////////////////////////////////////////////////////////////////// #
# Reddit request cog
# //////////////////////////////////////////////////////////////////////////// #
# Getting information from reddit
# //////////////////////////////////////////////////////////////////////////// #


class Reddit_Requester(comms.Cog):

    def __init__(self, bot):
        """ Object(s):
        Bot
        Background task
        """
        self.bot = bot
        self.load_script = self.bot.loop.create_task(self.load_reddit_script())

    def cog_unload(self):
        """
        Cancel background task(s) when cog is unloaded
        """
        self.load_script.cancel()

    """

    Background tasks

    """
    async def load_reddit_script(self):
        """
        Checks if reddit is accessable
        """
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.reddit_script_active = False
            printc('[...]: CHECKING REDDIT SCRIPT CREDENTIALS')
            f = json.load(open(path('relay', 'configuration', 'config.json')))['reddit']
            client_auth = requests.auth.HTTPBasicAuth(f['client_ID'], f['client_secret'])
            post_data = {"grant_type": "password", "username": f['username'], "password": f['password']}
            headers = {"User-Agent": f"Relay.py/{relay.__version__} by {f['username']}"}
            response = (requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)).json()
            reset_time = response['expires_in']
            self.headers = {"Authorization": f"{response['token_type']} {response['access_token']}", "User-Agent": f"Relay.py/{relay.__version__} by {f['username']}"}
            response = requests.get('https://oauth.reddit.com/api/v1/me', headers=self.headers)
            if response.json() in [{'message': 'Unauthorized', 'error': 401}, {'error': 'invalid_grant'}]:
                printc('WARNING: REDDIT ACCOUNT CANNOT BE ACTIVATED')
                await asyncio.sleep(60)
            else:
                self.reddit_script_active = True
                printc('[ ! ]: REDDIT SCRIPT CREDENTIALS ACTIVATED')
                await asyncio.sleep(reset_time + 1)

    """

    Commands

    """
    @comms.group(name='r/')
    async def subreddit_requests(self, ctx):
        """
        Subreddit group command
        """
        if ctx.invoked_subcommand is None:
            pass

    @subreddit_requests.command(name='info')
    async def subreddit_top(self, ctx, subreddit):
        """
        Request subreddit information
        """
        if self.reddit_script_active:
            response = (requests.get(f'https://oauth.reddit.com/r/{subreddit}/top/', {"limit": 1}, headers=self.headers)).json()
            # await ctx.send(response)
            print(response)

    @comms.group(name='u/')
    async def reddit_user_requests(self, ctx):
        """
        Reddit user group command
        """
        if ctx.invoked_subcommand is None:
            pass

    @reddit_user_requests.command(name='info')
    async def reddit_user_info(self, ctx, user):
        """
        Request reddit user information
        """
        if self.reddit_script_active:
            response = (requests.get(f'https://oauth.reddit.com/user/{user}/about/', headers=self.headers)).json()
            data = response['data']
            embed = discord.Embed(title=f'About reddit user {user}:', colour=0xc27c0e, timestamp=now())
            embed.add_field(name='Link to user profile', value=f'[/u/{user}](https://www.reddit.com/u/{user})')
            embed.set_thumbnail(url=data['icon_img'])
            embed.add_field(name='Karma', value=f"Link Karma: {data['link_karma']}, Comment Karma: {data['comment_karma']}")
            embed.set_footer(text=f'Python {platform.python_version()} with discord.py rewrite {discord.__version__}', icon_url='http://i.imgur.com/5BFecvA.png')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reddit_Requester(bot))
