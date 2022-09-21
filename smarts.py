import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime
import data_functions as db
import json
import time
import pytz
load_dotenv(find_dotenv())
token = os.getenv('TOKEN')
bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())
global msg
# Time format
def format_time(type):
    htime = db.get_time(type)
    if htime == 0:
        return '12:00 AM'
    elif htime > 0 and htime < 10:
        return f'0{str(htime)}:00 AM'
    elif htime > 9 and htime < 13:
        return f'{str(htime)}:00 PM'
    elif htime > 12 and htime < 22:
        return f'0{str(htime - 12)}:00 PM'
    elif htime > 21:
        return f'{str(htime - 12)}:00 PM'
    else:
        return f'{str(htime)}:00'

class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await tree.sync()
        self.synced = True
        print(f"Bot is online as {bot.user.display_name}")
        activity = discord.Game(name= f"Smart S on top", type=3)
        await bot.change_presence(status=discord.Status.idle, activity=activity)
bot = abot()
tree= app_commands.CommandTree(bot)

# Task loop
@tasks.loop(seconds= 1)
async def day_loop():
    guild = discord.Object(id=1020044841922609313)
    zone = pytz.timezone('Africa/Cairo')
    now = datetime.now(zone)
    if now.hour == db.get_time('open'):
        for channel in db.load_channels():
            await bot.get_channel(channel).set_permissions(bot.guilds[0].default_role, view_channel=True)
        embed = discord.Embed(
            title= "تم فتح رومات البيع",
            description= f"تغلق الرومات في  : {format_time('close')}",
            colour= discord.Colour.random()
            )
        embed.set_author(name=f"{bot.user.display_name}", icon_url=bot.user.display_avatar)
        await msg.edit(content="**||@here|| تم فتح رومات البيع**", embed=embed)
        await bot.get_channel(db.get_updates()).send('||@here||', delete_after=1)
        await asyncio.sleep(60*61)
    elif now.hour == db.get_time('close'):
        for channel in db.load_channels():
            await bot.get_channel(channel).set_permissions(bot.guilds[0].default_role, view_channel=False)
            await bot.get_channel(channel).purge()
        embed = discord.Embed(
            title= "تم غلق رومات البيع",
            description= f"تفتح الرومات في : {format_time('open')}",
            colour= discord.Colour.random()
            )
        embed.set_author(name=f"{bot.user.display_name}", icon_url=bot.user.display_avatar)
        await msg.edit(content="||@here|| **تم غلق رومات البيع**", embed=embed)
        await bot.get_channel(db.get_updates()).send('||@here||', delete_after=1)
        await asyncio.sleep(60*61)


# Set Open
@tree.command(name="setopen", description= "تحديد وقت فتح الرومات")
@app_commands.choices(choices=[
    app_commands.Choice(name="AM", value="am"),
    app_commands.Choice(name="PM", value="pm")
])
async def self(interation: discord.Interaction, time:str, choices:app_commands.Choice[str]):
    if interation.user.guild_permissions.administrator:
        if choices.value == "pm":
            entry= int(time) + 12
        else:
            entry= time
        if db.set_open(entry):
            await interation.response.send_message(f"Channels open time set to {str(time)}{choices.name}")
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

# Set Close
@tree.command(name="setclose", description= "تحديد وقت غلق الرومات")
@app_commands.choices(choices=[
    app_commands.Choice(name="AM", value="am"),
    app_commands.Choice(name="PM", value="pm")
])
async def self(interation: discord.Interaction, time:str, choices:app_commands.Choice[str]):
    if interation.user.guild_permissions.administrator:
        if choices.value == "pm":
            entry= int(time) + 12
        else:
            entry= time
        if db.set_close(entry):
            await interation.response.send_message(f"Channels open time set to {str(time)}{choices.name}")
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

# Set Updates Channel
@tree.command(name="setupdate", description= "تحديد روم التحديثات")
async def self(interation: discord.Interaction, channel:discord.TextChannel):
    if interation.user.guild_permissions.administrator:
        if db.set_updates(roomid=channel.id):
            await interation.response.send_message(f"Current updates channel is <#{channel.id}>")
            global msg
            msg = await bot.get_channel(db.get_updates()).send("**تظهر التحديثات هنا**")
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

# Add channel 
@tree.command(name="addchannel", description= "إضافة روم لقائمة الرومات")
async def self(interation: discord.Interaction, channel:discord.TextChannel):
    if interation.user.guild_permissions.administrator:
        channels= db.load_channels()
        if int(channel.id)not in channels:
            if db.add_room(channel.id):
                await interation.response.send_message(f"Channel <#{channel.id}> added to channels list")
        else:
            await interation.response.send_message(f"Channel <#{channel.id}> is already exist")
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

# reset database
@tree.command(name="reset", description= "إعادة قاعدة البيانات للاعدادات الافتراضية")
async def self(interation: discord.Interaction):
    if interation.user.guild_permissions.administrator:
        if db.reset(all=True):
            await interation.response.send_message(f"Done")
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

# Start
@tree.command(name="automatic", description= "بدء بوت فتح وغلق الرومات التلقائي ( مع العلم ان هذا الأمر يقوم بتعطيل جميع الأوامر)")
@app_commands.choices(action=[
    app_commands.Choice(name="Start", value="start"),
    app_commands.Choice(name="Stop", value="stop")
])
async def self(interation: discord.Interaction, action:app_commands.Choice[str]):
    if interation.user.guild_permissions.administrator:
        if action.value == 'start':
            await interation.response.send_message(f"Bot started | Current time {datetime.now(pytz.timezone('Africa/Cairo')).strftime('%H:%M')}", ephemeral=True)
            day_loop.start()
        if action.value == 'stop':
            await interation.response.send_message(f"Bot Stopped | Current time {datetime.now().strftime('%H:%M')}", ephemeral=True)
            day_loop.stop()
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)


@tree.command(name="close_channels", description= "غلق جميع الرومات")
async def self(interation: discord.Interaction):
    if interation.user.guild_permissions.administrator:
        await interation.response.send_message(f"Done", ephemeral=True)
        for channel in db.load_channels():
            await interation.guild.get_channel(channel).set_permissions(interation.guild.default_role, view_channel=False)
            await interation.guild.get_channel(channel).purge()
        embed = discord.Embed(
            title= "تم غلق رومات البيع",
            colour= discord.Colour.red()
        )
        embed.set_author(name=f"{bot.user.display_name}", icon_url=bot.user.display_avatar)
        await msg.edit(content="||@here|| **تم غلق رومات البيع**", embed=embed)
        await bot.get_channel(db.get_updates()).send('||@here||', delete_after=1)
    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

@tree.command(name="open_channels", description= "فتح جميع الرومات")
async def self(interation: discord.Interaction):
    if interation.user.guild_permissions.administrator:
        await interation.response.send_message(f"Done", ephemeral=True)
        for channel in db.load_channels():
            await interation.guild.get_channel(channel).set_permissions(interation.guild.default_role, view_channel=True)
        embed = discord.Embed(
            title= "تم فتح رومات البيع",
            colour= discord.Colour.random()
        )
        embed.set_author(name=f"{bot.user.display_name}", icon_url=bot.user.display_avatar)
        await msg.edit(content="**||@here|| تم فتح رومات البيع**", embed=embed)
        await bot.get_channel(db.get_updates()).send('||@here||', delete_after=1)

    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

@tree.command(name="list", description= "عرض جميع الرومات المتحكم بها")
async def self(interation: discord.Interaction):
    if interation.user.guild_permissions.administrator:
        dsc = f"""**روم التحديثات:**\n
        > <#{db.get_updates()}>\n\n**رومات البيع/الطلب:**\n\n"""
        for room in db.load_channels():
            dsc += f"> <#{room}>\n\n"
        embed = discord.Embed(
            title= "الرومات المتحكم بها",
            description=dsc,
            colour= discord.Colour.random()
        )
        embed.set_author(name=f"{bot.user.display_name}", icon_url=bot.user.display_avatar)
        await interation.response.send_message(embed=embed)

    else:
        await interation.response.send_message(f"You are not an admin", ephemeral=True)

if __name__== "__main__":
    bot.run(token)
