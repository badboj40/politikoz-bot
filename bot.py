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

CHANNEL = 889811646858526730

client = discord.Client()
most_recent = dict()
debug = False
#assets = sorted(assets, key = lambda i: -i['dateSold'])



settings_recently_sold = {
	'sort': 'date',
	'order': 'desc',
	'sold': 'true',
	'max pages': 1,
}
settings_all_assets = {
	'sort': 'price',
	'order': 'asc',
	'sold': 'false',
	'max pages': 1000,
}


async def recently_sold(channel):
	global most_recent
	recent25 = tools.get_assets(settings_recently_sold)
	recent25_sorted = sorted(recent25, key = lambda i: i['dateSold'])
	if bool(most_recent):
		for asset in recent25_sorted:
			if debug or asset['dateSold'] > most_recent['dateSold']:
				embedVar = tools.format_message(asset)
				await channel.send(embed=embedVar)
	most_recent = recent25_sorted[-1]
	

async def background_task():
	await client.wait_until_ready() # ensures cache is loaded
	channel = client.get_channel(id=CHANNEL)
	while not client.is_closed():
		await recently_sold(channel)
		assets = tools.get_assets(settings_all_assets)
		tools.save_to_file(assets)	
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
		response = tools.get_floor(message.content[6:].strip())
		await message.channel.send(response)

client.run(TOKEN)

