import discord
from discord.ext import commands
import music
import os  

cogs = [music]

client = commands.Bot(command_prefix='-', intents = discord.Intents.all())

client.embed_color = 0x000000#2bc423

for i in range(len(cogs)):
    cogs[i].setup(client)

@client.event
async def on_message_edit(before, after):
    await client.process_commands(after)


client.run("Token")
