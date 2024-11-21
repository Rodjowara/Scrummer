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
intents.members = True

info = Info()
setup_done = 0
server_name = None
wokenup = 0

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command(name= 'wakeup')
async def wakeup(ctx):
    global setup_done
    global wokenup
    global server_name

    server_name = str(ctx.guild)
    await ctx.send(f'Hello, {server_name}!')

    wokenup = 1

    #ovo rješenje funkcionira samo kad je bot u jednom serveru
    #TODO: za bota koji je u više servera
    #maaybe da se provjeri formating filea? Da nam ne bi zločesti programer podvalio nešto

    file_name = 'setup_' + server_name + '.txt'

    if os.path.isfile(file_name):
        print('Dosao u os.path.isfile')
        setup_done = 1
        with open(file_name, 'r') as file:
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
    global setup_done
    global server_name
    global wokenup

    if not wokenup:
        await wakeup(ctx)

    if setup_done:
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

    lines = [line for line in text if line.strip()]
    line_count = len(lines)
    if line_count < (info.member_count + 3):
        await ctx.send('Missing info in the file. Send the file with all required information (start and end dates, meeting time, and roles for all members')
        return

    message = None

    i = 0
    for line in text.splitlines():
        line = line.split('-')

        if line[0] == 'role':
            rolegiver = line[1].split(':')
            user = rolegiver[0]
            role = rolegiver[1]
            role_disc = discord.utils.get(ctx.guild.roles, name = role)
            if not role_disc:
                await ctx.send(f"Role '{role}' not found in server.")
            member = discord.utils.get(ctx.guild.members, name = user)
            if member:
                try:
                   await member.add_roles(role_disc)
                   await ctx.send(f"Added role '{role_disc}' to user '{member.display_name}'.")
                except discord.Forbidden:
                    await ctx.send(f"Permission to add role '{role_disc}' to user '{member.display_name}'")
                except discord.HTTPException as e:
                    await ctx.send(f"Failed to add role '{role_disc}' to {member.display_name}: {e}")
            else:
                await ctx.send(f"User '{user}' not yet in server.")

        if line[0] == 'startdate':
            info.startdate = line[1]
            i += 1
            message = (f'Start date for the project is {info.startdate}\n')
        
        if line[0] == 'enddate':
            info.enddate = line[1]
            i += 1
            message += (f'End date for the project is {info.enddate}\n')

        if line[0] == 'meeting_time':
            i += 1
            info.meeting_time = line[1]
            message += (f'Meeting time for this project is {info.meeting_time}\n')

    if i != 3:
        await ctx.send('Invalid file sent. Please send a valid setup file.')
        return

    await ctx.send(message)
    try:
        async for message in ctx.channel.history(limit=1):
            await message.pin()
            return
        await ctx.send("No messages found in this channel.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to pin messages.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to pin the message due to an error: {e}")

    file_name = 'setup_' + server_name + '.txt'
    with open(file_name, 'a') as file:
        file.write(f'server_name:{info.server_name}\n')
        file.write(f'member_count:{info.member_count}\n')
        file.write(f'startdate:{info.startdate}\n')
        file.write(f'enddate:{info.enddate}\n')
        file.write(f'meeting_time:{info.meeting_time}\n')

    setup_done = 1

@bot.command(name= "voice")
async def voice(ctx, channel_name: str):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
    
    if not voice_channel:
        await ctx.send(f"Voice channel '{channel_name}' not found.")
        return

    members = voice_channel.members

    if members:
        member_names = ", ".join([member.display_name for member in members])
        with open('meeting.txt', 'w') as file:
            file.write(member_names)
    else:
        with open('meeting.txt', 'w') as file:
            file.write(f"No members are currently in '{channel_name}'.")

    try:
        await ctx.send(file=discord.File('meeting.txt'))
    except Exception as e:
        await ctx.send(f"Error sending file: {e}")


bot.run(TOKEN)