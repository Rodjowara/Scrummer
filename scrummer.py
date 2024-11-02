import discord
from discord.ext import commands
import os

class Info:
    server_name = None
    member_count = None
    startdate = None
    enddate = None
    meeting_time = None

TOKEN = "MTMwMDQwNDk3OTQyMDM2ODkxNw.GY_yyw.nZjvzf-4KDxCtGfxm0CQ6Chm-BUIWLrpDuzqGE"
intents = discord.Intents.default()
intents.message_content = True

info = Info()
setup_done = 0

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():

    #ovo rješenje funkcionira samo kad je bot u jednom serveru
    #TODO: za bota koji je u više servera
    #maaybe da se provjeri formating filea? Da nam ne bi zločesti programer podvalio nešto
    if os.path.isfile('setup.txt'):
        setup_done = 1
        with open('setup.txt', 'r') as file:
            line = file.readline().strip().split(':')
            info.server_name = line[1]

            line = file.readline().strip().split(':')
            info.member_count = line[1]

            line = file.readline().strip().split(':')
            info.startdate = line[1]

            line = file.readline().strip().split(':')
            info.enddate = line[1]

            line = file.readline().strip().split(':')
            info.meeting_time = line[1]

    print(f'{bot.user} has connected to Discord')

@bot.command(name="hello")
async def greet(ctx):
    await ctx.send(f'Hello, {ctx.author.name}')

@bot.command(name="setup")
async def setup(ctx):

    if not setup_done:
        await ctx.send('Setup is already completed')
        return

    info.server_name = ctx.guild
    info.member_count = info.server_name.member_count

    if not ctx.message.attachments:
        await ctx.send("Please attach a .txt file.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith('.txt'):
        await ctx.send("Please attach a valid .txt file.")
        return

    file_content = await attachment.read()
    text = file_content.decode('utf-8')

    with open(text, 'r') as file:
        lines = [line for line in file if line.strip()]
        line_count = len(lines)
        if line_count < (info.member_count + 3):
            await ctx.send('Missing info in the file. Send the file with all required information (start and end dates, meeting time, and roles for all members')
            return

    i = 0
    for line in text.splitlines():
        line = line.split('-')

        if line[0] == 'role':
            rolegiver = line[1].split(':')
            user = rolegiver[0]
            role = rolegiver[1]
            await ctx.send(f'{user} gets the role {role}')

        if line[0] == 'startdate':
            info.startdate = line[1]
            i += 1
            await ctx.send(f'Start date for the project is {info.startdate}')
        
        if line[0] == 'enddate':
            info.enddate = line[1]
            i += 1
            await ctx.send(f'End date for the project is {info.enddate}')

        if line[0] == 'meeting_time':
            i += 1
            info.meeting_time = line[1]
            await ctx.send(f'Meeting time for this project is {info.meeting_time}')

    if i != 3:
        await ctx.send('Invalid file sent. Please send a valid setup file.')
        return

    with open('setup.txt', 'a') as file:
        file.write(f'server_name:{info.server_name}')
        file.write(f'member_count:{info.member_count}')
        file.write(f'startdate:{info.startdate}')
        file.write(f'enddate:{info.enddate}')
        file.write(f'meeting_time:{info.meeting_time}')

    setup_done = 1

bot.run(TOKEN)