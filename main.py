import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='-', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)



client.run("OTIzNTc5ODc1OTEzMjYxMDg3.YcSEyQ.r1kiqSAQJjwfETFcNc5FSnANY10")
