# bot.py
import os
import discord
from dotenv import load_dotenv
import asyncio

import tools

SECONDS_BETWEEN_REFRESH = 300

load_dotenv()

# you have to make a file in the same directory called ".env"
# in this file you have to put the three variables like this:

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = int(os.getenv('TEXT_CHANNEL'))


client = discord.Client()
most_recent = dict()
debug = True
#assets = sorted(assets, key = lambda i: -i['dateSold'])

settings_recently_sold = {
    'sort': '_id:-1',
    'type': 'sold',
    'max pages': 1,
    'sold': 'true',
}
settings_all_assets = {
    'sort': 'price:1',
    'type': 'listing',
    'max pages': 1000,
    'sold': 'false',
}


async def recently_sold(channel):
    global most_recent
    recent25 = tools.get_assets(settings_recently_sold)
    if debug:
        embedVar = tools.format_message(recent25[0])
        await channel.send(embed=embedVar)
    elif bool(most_recent):
        for asset in recent25:
            if asset['epoch_time'] > most_recent['epoch_time']:
                embedVar = tools.format_message(asset)
                await channel.send(embed=embedVar)
            else:
                break
    if recent25:
        most_recent = recent25[0]
	

async def background_task():
    await client.wait_until_ready() # ensures cache is loaded
    channel = client.get_channel(id=CHANNEL)
    while not client.is_closed():
        await recently_sold(channel)
        await asyncio.sleep(SECONDS_BETWEEN_REFRESH)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    client.loop.create_task(background_task())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content[:6].strip().lower() == '/floor':
        embedVar = tools.get_floor(message.content[6:].strip())
        await message.channel.send(embed=embedVar)

client.run(TOKEN)

