import discord
import os
import platform
import requests

from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix = '!', intents=intents)

load_dotenv()

@client.event
async def on_ready():
    print("Bot is ready for use")


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.command()
async def weather(ctx):
    response = requests.get('https://api.weather.gov/gridpoints/BOX/74,59/forecast')
    data = response.json()
    forecast = data['properties']['periods'][0]
    await ctx.send(f"Weather in Lowell, MA: {forecast['shortForecast']}, {forecast['temperature']}°{forecast['temperatureUnit']}")

@client.command()
async def info(ctx):
    os_info = platform.uname()
    await ctx.send(f"Operating System: {os_info.system}\n"
                   f"Release: {os_info.release}\n"
                   f"Version: {os_info.version}\n"
                   f"Machine: {os_info.machine}\n"
                   f"Processor: {os_info.processor}")



client.run(os.getenv('TOKEN'))