import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='-', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

@client.event
async def on_message_edit(before, after):
    await client.process_commands(after)

client.run("Token")
