import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from yt_dlp import YoutubeDL
import requests
import random
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
ROLENAME = os.getenv("ROLENAME")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

# Dice roller
@bot.command(name='roll', help='Rolls a die, accepts 1 argument for sides, default 6')
@commands.has_role(ROLENAME)
async def roll(ctx, number_of_sides = 6):

    response = random.choice(range(1, number_of_sides + 1))
    await ctx.send(response)


# Coin flipper
@bot.command(name='flip', help='Flips a coin')
@commands.has_role(ROLENAME)
async def flip(ctx):
    faces = [
        "Heads","Tails"
    ]
    
    response = random.choice(faces)
    await ctx.send(response)

# Join VC
@bot.command(name='play', help='Plays the requested song in the VC of the person who called the command')
@commands.has_role(ROLENAME)
async def play(ctx, url):
    if ctx.author.voice:
        user_channel = ctx.author.voice.channel
        await user_channel.connect()
    
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice = get(bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['url']
            voice.play(FFmpegPCMAudio(executable=FFMPEG_PATH, source=URL, **FFMPEG_OPTIONS))
            voice.is_playing()
            await ctx.send('Bot is playing')

    # check if the bot is already playing
        else:
            await ctx.send("Bot is already playing")
            return
    else:
        await ctx.send('Join a voice channel then run this command again.')


# command to resume voice if it is paused
@bot.command(name='resume', help='Resumes audio')
@commands.has_role(ROLENAME)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


# command to pause voice if it is playing
@bot.command(name='pause', help='Pauses audio')
@commands.has_role(ROLENAME)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@bot.command(name='stop', help='Stops audio')
@commands.has_role(ROLENAME)
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')



# Disconnects from channel
@bot.command(name='leave', help='Leaves the current VC')
@commands.has_role(ROLENAME)
async def leave(ctx):
   
   await ctx.voice_client.disconnect()


# Check ping
@bot.command(name='ping', help='Displays the ping')
@commands.has_role(ROLENAME)
async def ping(ctx):
    ping_ = bot.latency
    ping =  round(ping_ * 1000)
    await ctx.send(f"Ping is {ping}ms")

bot.run(TOKEN)