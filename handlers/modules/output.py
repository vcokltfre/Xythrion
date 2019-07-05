"""
>> Xiux
> Copyright (c) 2019 Xithrius
> MIT license, Refer to LICENSE for more info
"""


import __main__
import datetime
import os
import aiohttp


def path(*objects):
    """ Returns path relative to caller file location with additional objects, if any """
    newPath = ((__main__.__file__).split(os.sep))[:-1]
    for i in objects:
        newPath.append(i)
    return (os.sep).join(str(y) for y in newPath)


def printc(string):
    """ Customized printing to the console with timestamps """
    now = datetime.datetime.now()
    print(f"~> [{now}] {string}")


def duplicate(string: str):
    """ Prints to console and wherever else """
    printc(string)
    return (string[string.index(':') + 2]).upper() + (string[string.index(':') + 3]).lower()


def sectional_print(loaded_cogs):
    """ Prints cogs out in sections """
    all_cogs, sectioned_cogs = [], []
    l_cogs = [x.split('.')[-2:] for x in loaded_cogs]
    for i in range(len(l_cogs) - 1):
        x = [j for j, v in enumerate([x[0] for x in l_cogs]) if v == l_cogs[i][0]]
        if x not in sectioned_cogs:
            sectioned_cogs.append(x)
    for i in range(len(sectioned_cogs)):
        within_cogs = [l_cogs[sectioned_cogs[i][0]][0], [l_cogs[j][1] for j in sectioned_cogs[i]]]
        all_cogs.append(within_cogs)
    for i in all_cogs:
        print(f'\t{i[0]}: {", ".join(str(y) for y in i[1])}')


def now():
    """ Returns the time depending on time zone from file """
    return datetime.datetime.now()


def progressBar(amount, total):
    x = '█'


async def aiohttp_requester(option, ctx, url, headers, data=None):
    """ Gets data from a REST API """
    async with aiohttp.ClientSession() as session:
        if option == 'GET':
            async with session.get(url, headers=headers, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    await ctx.send(f'Status {response.status}: Requester unavailable')
        elif option == 'POST':
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    await ctx.send(f'Status {response.status}: Requester unavailable')
