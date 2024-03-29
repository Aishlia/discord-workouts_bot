from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import datetime
import time
import discord
from discord.ext import commands

from interval_timer import IntervalTimer
from voice_announcer import VoiceAnnouncer


bot = commands.Bot(command_prefix='!')
timer = IntervalTimer()
voice_announcer = None

@bot.event
async def on_ready():
    print(f'The bot has logged in as {bot.user} and is ready to serve requests of its human overlords.')


@bot.command(name='hello', help='Responds with a hello message to show bot is up.')
async def greeting(context):
    await context.send('Hello there!')


@bot.command(name='start', help='Starts the timer with specified settings. (exercises, sets, workout_time, workout_rest, set_rest, halway_sound: bool)')
async def start_timer(context, exercises: int, sets: int, workout_time: int, workout_rest: int, set_rest: int, halfway_sound=False):
    if halfway_sound == True and workout_time <= 10:
        await context.send('Halway timer is only allowed for workout times greater than 10 seconds. It has been disabled.')
    global timer
    # We can only run one timer at the same time.
    if timer.running():
        await context.send('Timer is already running, please stop it first.')
        return

    timer.start(exercises, sets, workout_time, workout_rest, set_rest, halfway_sound)
    await context.send(f'Beginning {timer.print_config()}. HAVE FUN!')

@bot.command(name='restart', help='Restart the timer with previous settings.')
async def restart_timer(context):
    global timer
    if timer.running():
        await context.send('Timer is already running, please stop it first.')
        return

    timer.restart()
    await context.send(f'Here we go again... {timer.print_config()} for you.')


@bot.command(name='stop', help='Stops the timer currently running.')
async def stop_timer(context):
    global timer
    if not timer.running():
        await context.send('There is no timer running, so let\'s call this a success, shall we?')
        return

    timer.stop()
    await context.send('Timer stopped.')


@bot.command(name='show', help='Shows the current settings for the timer.')
async def show_timer_config(context):
    global timer
    await context.send('Let\'s see...')
    await context.send(f'The timer is set for {timer.print_config()}.')
    await context.send('If that\'s okay for you, just restart the timer, otherwise tell me something new.')


@bot.command(name='voice', help='Instructs the bot to join the voice channel you are in.')
async def join_voice(context: commands.Context):
    # Not sure how to do this nicely, in other languages I would use the null-conditional operator on voice
    voice_channel = context.author.voice.channel if context.author.voice is not None else None

    if voice_channel is None:
        await context.send('Oh my, I do not know where to go.')
        await context.send('Please join a voice channel and I will follow you.')
        return

    voice_client = await voice_channel.connect()

    global voice_announcer, timer
    voice_announcer = VoiceAnnouncer(voice_client)
    voice_announcer.attach(timer)


@bot.command(name='mute', help='Instructs the bot to leave its voice channel.')
async def leave_voice(context: commands.Context):
    global voice_announcer, timer
    voice_announcer.detach(timer)
    voice_announcer = None
    await context.voice_client.disconnect()


@bot.command(name='reminder', help='Reminds users that it is workout time!')
async def reminder(context: commands.Context):
    await context.send('Reminder active')
    # first_ping = False
    # second_ping = False
    # workout_time = False

    while True:
        if datetime.datetime.now().hour == 22 and datetime.datetime.now().minute == 30:
            await context.send('@everyone 30 minutes to workout time')
            time.sleep(60*14)
        if datetime.datetime.now().hour == 22 and datetime.datetime.now().minute == 45:
            await context.send('@everyone 15 minutes to workout time')
            time.sleep(60*14)
        if datetime.datetime.now().hour == 23 and datetime.datetime.now().minute == 00:
            await context.send('@everyone WORKOUT TIME!!!!!')
        time.sleep(30)



bot.run(os.getenv('BOT_TOKEN'))
