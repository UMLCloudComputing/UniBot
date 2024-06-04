import discord
import os
from discord.ext import commands

intents = discord.Intents.all()
intents.messages = True
client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print("Bot is ready for use")


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


client.run(os.getenv('BOT_TOKEN'))