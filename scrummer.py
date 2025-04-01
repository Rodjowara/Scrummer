import discord
from discord.ext import commands
from datetime import date, datetime, timedelta, time
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class Info:
    server_name = None
    member_count = None
    startdate = None
    enddate = None
    meeting_time = None
    current_week = None
    progress_channel = None

TOKEN = "MTMwMDQwNDk3OTQyMDM2ODkxNw.GY_yyw.nZjvzf-4KDxCtGfxm0CQ6Chm-BUIWLrpDuzqGE"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
scheduler = AsyncIOScheduler()

info = Info()
setup_done = 0
server_name = None
wokenup = 0
index = 0

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command(name= 'wakeup')
async def wakeup(ctx):
    global setup_done
    global wokenup
    global server_name

    server_name = str(ctx.guild)
    await ctx.send(f'Hello, {server_name}!')

    wokenup = 1

    file_name = 'setup_' + server_name + '.txt'

    if os.path.isfile(file_name):
        setup_done = 1
        lines = None
        with open(file_name, 'r') as file:
            lines = file.readlines()
            file.seek(0)

            line = file.readline().strip().split(':')
            info.server_name = line[1]

            line = file.readline().strip().split(':')
            info.member_count = line[1]

            line = file.readline().strip().split(':')
            info.startdate = line[1]

            line = file.readline().strip().split(':')
            info.enddate = line[1]

            line = file.readline().strip().split(':')
            meeting_time = [line[1], line[2]]
            info.meeting_time = ':'.join(meeting_time)

            line = file.readline().strip().split(':')
            info.progress_channel = line[1]

        week_number = date.today().isocalendar()[1]
        tempdate = datetime.strptime(info.startdate, "%d.%m.%Y.").date().isocalendar()[1]
        current_week = week_number - tempdate

        if current_week < 0:
            current_week = 52 - tempdate + week_number

        if current_week != info.current_week:
            lines[6] = "current_week:" + str(current_week) + "\n"
            info.current_week = current_week
            with open(file_name, 'w') as file:
                for line in lines:
                    line = ''.join(line)
                    file.write(line)
            with open("progress.txt", 'a') as file:
                file.write('\n')
                wrote = "Week " + str(current_week) + ":\n"
                file.write(wrote)

    start = info.startdate.split(".")
    times = info.meeting_time.split(":")

    # start_time = datetime(start[2], start[1], start[0], time[0], time[1])
    # scheduler.add_job(progress_report, 'interval', weeks=1, start_date = start_time)

    start_time = datetime.now()
    scheduler.add_job(progress_report, 'interval', minutes=2, start_date=start_time)

    scheduler.start()

    send_time = info.meeting_time.split(':')
    hours = int(send_time[0])
    minutes = int(send_time[1])
    target_time = time(hour=hours, minute=minutes)
    times = (datetime.combine(datetime.today(), target_time) - timedelta(minutes=30))
    
    GUILD_ID = None
    GUILD_OWNER = None
    for guild in bot.guilds:
        if guild.name == info.server_name:
            GUILD_ID = guild.id
            GUILD_OWNER = guild.owner
            break

    # scheduler.add_job(
    #     bugreport,
    #     CronTrigger(hour=time.hour, minute=time.minute),
    #     args=[GUILD_ID, GUILD_OWNER]
    # )

    scheduler.add_job(
        bugreport,
        CronTrigger(minute='*/2'), 
        args=[GUILD_ID, GUILD_OWNER]
    )

    print(f'{bot.user} has connected to Discord')    

@bot.command(name="setup")
async def setup(ctx):
    global setup_done
    global server_name
    global wokenup

    if setup_done:
        await ctx.send('Setup is already completed')
        return

    info.server_name = str(ctx.guild)
    server_name = str(ctx.guild)
    info.member_count = ctx.guild.member_count

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
        await ctx.send('Missing info in the file. Send the file with all required information (start and end dates, meeting time, progress channel, and roles for all members')
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
        
        if line[0] == 'progress_channel':
            i += 1
            channel_name = line[1]
            for channel in ctx.guild.channels:
                if channel.name == channel_name:
                    info.progress_channel = channel.id
                    message += (f'Progress channel for this project is {channel_name}\n')
            
            if not info.progress_channel:
                await ctx.send('The channel does not exist. Please enter a valid channel')
                return

            message += (f'Progress channel for this project is {info.progress_channel}\n')

    if i != 4:
        await ctx.send('Invalid file sent. Please send a valid setup file.')
        return

    await ctx.send(message)
    try:
        async for message in ctx.channel.history(limit=1):
            await message.pin()
        #await ctx.send("No messages found in this channel.")
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
        file.write(f'progress_channel:{info.progress_channel}\n')
        file.write(f'current_week:1\n')

    # start = info.startdate.split(".")
    # time = info.meeting_time.split(":")

    #start_time = datetime(start[2], start[1], start[0], time[0], time[1])
    #scheduler.add_job(progress_report, 'interval', weeks=1, start_date = start_time)

    start_time = datetime.now()
    scheduler.add_job(progress_report, 'interval', minutes=2, start_date=start_time)

    scheduler.start()

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

@bot.command(name= "todo")
async def todo(ctx, priority: int, *, user_message: str):
    
    global setup_done
    if not setup_done:
        await wakeup(ctx)

    if priority < 1 or priority > 3:
        await ctx.send("Priority out of range. Priority should be between 1 and 3")
        return

    global index
    message = [None, priority, user_message]
    filename = str(date.today()) + ".txt"
    lines = None
    place = 0

    if not os.path.exists(filename):
        open(filename, "x")
        index = 0
    elif not index:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                index += 1

    index = index + 1
    message[0] = index

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split()
            if int(line[1]) < priority:
                break
            else:
                place += 1

    write = " ".join(map(str, message))
    write += "\n"
    lines.insert(place, write)

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(lines)
    
    with open("progress.txt", 'a', encoding="utf-8") as file:
        report = "Reported bug " + str(message[0]) + ", description: " + str(message[2]) + "\n"
        file.write(report)    

    await ctx.send(f"Task {index} successfully submitted")

@bot.command(name="progress")
async def progress(ctx, id: int):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    lines = None
    found = 0
    with open("progress.txt", 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.split(',')
        line = line[0].split()
        if int(line[2]) == id:
            found = 1
            break
    
    if found:
        with open("progress.txt.", 'a') as file:
            message = "Resolved bug number " + str(id) + "\n"
            file.write(message)
    else:
        await ctx.send("Bug not found. Please check if the id is correct.")

@bot.command(name="report")
async def report(ctx, name, *reason):

    global setup_done
    if not setup_done:
        await wakeup(ctx)
    
    for guild in bot.guilds:
        if(guild.name == server_name):
            for member in guild.members:
                if(member == name):

                    with open("reports.txt", 'a') as file:
                        file.write(f"Reported member {name} for reason: {reason}")

                    break
            break

@bot.command(name="file")
async def file(ctx, file):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    if(os.path.exists(file) and file != "all"):
        await ctx.send(f"File {file} doesn't exist.")
        return

    if(file == "progress.txt"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File("progress.txt"))
    elif(file == "reports.txt"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File("reports.txt"))
    elif(file == "todo"):

        await ctx.send("Here are your todo files: ")
        for filename in os.listdir("."):
            if filename.endswith(".txt"):
                try:
                    date_part = filename.split(".")[0] 
                    parsed_date = datetime.strptime(date_part, "%Y-%m-%d")
                    await ctx.send(file = discord.File(filename))
                except ValueError:
                    await ctx.send("There are no todo files currently")

    elif(file == "all"):
        await ctx.send("Here are all your files: ")
        for filename in os.listdir("."):
            if filename.endswith(".txt"):
                await ctx.send(file = discord.File(filename))
    
    else:
        await ctx.send("There are no such files currently")
    


async def progress_report():

    now = datetime.now()
    end = info.enddate.split(".")
    time = info.meeting_time.split(":")
    endtime = datetime(int(end[2]), int(end[1]), int(end[0]), int(time[0]), int(time[1]))
    
    channel = bot.get_channel(info.progress_channel)

    if now > endtime:
        if channel:
            try:
                await channel.send("Here is this week's progress report:", file=discord.File("progress.txt"))
            except Exception as e:
                print(f"Failed to send file: {e}")
        else:
            print(f"Channel with ID {info.progress_channel} not found.")

        print("End date reached. Stopping file messages.")
        scheduler.remove_all_jobs()
        return
    
    if channel:
        try:
            await channel.send("Here is this week's progress report:", file=discord.File("progress.txt"))
        except Exception as e:
                print(f"Failed to send file: {e}")
    else:
        print(f"Channel with ID {info.progress_channel} not found.")
        

async def bugreport(id, owner):
    filename = str(date.today()) + ".txt"
    try:
        await owner.send("Here's your bugreport file: ", file = discord.File(filename))
        print(f"File sent to {owner.name} (server owner).")
    except Exception as e:
        print(f"Failed to send file to the server owner: {e}")

bot.run(TOKEN)