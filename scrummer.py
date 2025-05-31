import discord
from discord.ext import commands
from datetime import date, datetime, timedelta, time
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import re

class Info:
    server_name = None
    member_count = None
    startdate = None
    enddate = None
    meeting_time = None
    current_week = None
    progress_channel = None
    index = 0

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

working_directory = "C:/Users/rodak/Documents/zavrsni/files"

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command(name= 'wakeup')
async def wakeup(ctx):
    global setup_done
    global wokenup
    global server_name
    global working_directory

    os.chdir(working_directory)

    server_name = str(ctx.guild)
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

            line = file.readline().strip().split(':')
            info.current_week = line[1]

            line = file.readline().strip().split(':')
            info.index = int(line[1])

        week_number = date.today().isocalendar()[1]
        tempdate = datetime.strptime(info.startdate, "%d.%m.%Y.").date().isocalendar()[1]
        current_week = week_number - tempdate + 1

        if current_week < 0:
            current_week = 52 - tempdate + week_number

        if str(current_week) != info.current_week:
            print(f"Info.current week: {type(info.current_week)}")
            print(f"Current week: {type(current_week)}")
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

            lines = None
            with open(f"setup_{info.server_name}.txt", 'r') as file:
                lines = file.readlines()

            lines[-2] = f"current_week:{info.current_week}\n"
            with open(f"setup_{info.server_name}.txt", 'w') as file:
                file.writelines(lines)

    else:
        await ctx.send("Setup is not done yet")
        return

    start = info.startdate.split(".")
    times = info.meeting_time.split(":")

    # start_time = datetime(start[2], start[1], start[0], time[0], time[1])
    # scheduler.add_job(progress_report, 'interval', weeks=1, start_date = start_time)

    start_time = datetime.now()
    # scheduler.add_job(progress_report, 'interval', minutes=2, start_date=start_time)

    # scheduler.start()

    send_time = info.meeting_time.split(':')
    hours = int(send_time[0])
    minutes = int(send_time[1])
    target_time = time(hour=hours, minute=minutes)
    times = (datetime.combine(datetime.today(), target_time) - timedelta(minutes=30))
    
    # GUILD_ID = None
    # GUILD_OWNER = None
    # for guild in bot.guilds:
    #     if guild.name == info.server_name:
    #         GUILD_ID = guild.id
    #         GUILD_OWNER = guild.owner
    #         break

    # scheduler.add_job(
    #     bugreport,
    #     CronTrigger(hour=time.hour, minute=time.minute),
    #     args=[GUILD_ID, GUILD_OWNER]
    # )

    # scheduler.add_job(
    #     bugreport,
    #     CronTrigger(minute='*/2'), 
    #     args=[GUILD_ID, GUILD_OWNER]
    # )

    print(f'{bot.user} has connected to Discord')
    
    await ctx.send(f'Hello, {server_name}!')

    wokenup = 1

@bot.command(name="setup")
async def setup(ctx):
    global setup_done
    global server_name
    global wokenup
    global working_directory

    if setup_done:
        await ctx.send('Setup is already completed')
        return
    
    os.chdir(working_directory)

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

    week_number = date.today().isocalendar()[1]
    tempdate = datetime.strptime(info.startdate, "%d.%m.%Y.").date().isocalendar()[1]
    current_week = week_number - tempdate + 1

    if current_week < 0:
        current_week = 52 - tempdate + week_number
    
    info.current_week = current_week

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
        file.write(f'current_week:{info.current_week}\n')
        file.write(f'index:{info.index}\n')

    with open('progress.txt', 'w') as file:
        file.write(f"Week {info.current_week}:\n")

    # start = info.startdate.split(".")
    # time = info.meeting_time.split(":")

    #start_time = datetime(start[2], start[1], start[0], time[0], time[1])
    #scheduler.add_job(progress_report, 'interval', weeks=1, start_date = start_time)

    # start_time = datetime.now()
    # scheduler.add_job(progress_report, 'interval', minutes=2, start_date=start_time)

    # scheduler.start()

    setup_done = 1

@bot.command(name= "voice")
async def voice(ctx, channel_name: str):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

    if not voice_channel:
        await ctx.send(f"Voice channel '{channel_name}' not found.")
        return

    members = voice_channel.members

    now = datetime.now()
    time = f"{now.day:02}.{now.month:02}.{now.year:02},{now.hour:02}:{now.hour:02}"

    if members:
        member_names = " ".join([member.display_name for member in members])
        with open('meeting.txt', 'a') as file:
            file.write(f"{time},")
            file.write(f"{channel_name},")
            file.write(member_names)
            file.write("\n")
    else:
        with open('meeting.txt', 'a') as file:
            file.write(f"No members are currently in '{channel_name}'.\n")

    try:
        await ctx.send(file=discord.File('meeting.txt'))
    except Exception as e:
        await ctx.send(f"Error sending file: {e}")

@bot.command(name= "todo")
async def todo(ctx, priority: int, *, user_message: str):
    info.index += 1

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    if priority < 1 or priority > 3:
        await ctx.send("Priority out of range. Priority should be between 1 and 3")
        return

    message = [priority, info.index, user_message]
    filename = "todo_" + str(date.today()) + ".txt"
    lines = None
    place = 0

    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(",")
                if int(line[0]) < priority:
                    break
                else:
                    place += 1

        write = ",".join(map(str, message))
        write += "\n"
        lines.insert(place, write)

        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(lines)

    else:
        with open(filename, "w", encoding="utf-8") as file:
            write = ",".join(map(str, message))
            write += "\n"
            file.write(write)
    
    with open("progress.txt", 'a', encoding="utf-8") as file:
        report = f"{ctx.author} | Reported task | {str(message[2])} | {info.index} \n"
        file.write(report)    

    await ctx.send(f"Task {info.index} successfully submitted")

    lines = None
    with open(f"setup_{info.server_name}.txt", "r") as file:
        lines = file.readlines()
    
    lines[-1] = f"index:{info.index}"
    with open(f"setup_{info.server_name}.txt", "w") as file:
        file.writelines(lines)


@bot.command(name="progress")
async def progress(ctx, id = 0, *, description:str):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    now = datetime.now()
    time = f"{now.day:02}.{now.month:02}.{now.year:02}. {now.hour:02}:{now.hour:02}"

    with open("progress.txt.", 'a') as progress:
        if(id > 0):

            lines = None
            filename = f"workday_{ctx.author}.txt"
            with open(filename, 'r') as file:
                lines = file.readlines()

            found = False
            ind = -1
            for line in lines:
                ind += 1
                if(line.startswith("deadline")):
                    continue
                if(int(line.split(",")[2]) == id):
                    newline = line.split(",")
                    newline[2] = "0"
                    newline = ",".join(newline)
                    lines[ind] = newline
                    found = True
                    break
            
            if(found):
                message = f"{time} | {ctx.author} | Resolved task number {str(id)} | description: {description} \n"
                progress.write(message)

                with open(filename, 'w') as file:
                    file.writelines(lines)
            else:
                await ctx.send(f"Task with id {id} was not assigned to you")            

        else:
            message = f"{time} | {ctx.author} | {description} \n"
            progress.write(message)

@bot.command(name="report")
async def report(ctx, user: discord.User, *, reason:str):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    now = datetime.now()
    time = f"{now.day:02}.{now.month:02}.{now.year:02}. {now.hour:02}:{now.hour:02}"

    GUILD_OWNER = None
    for guild in bot.guilds:
        if guild.name == info.server_name:
            GUILD_OWNER = guild.owner
            break

    await GUILD_OWNER.send(f"User {user} has been reported for reason: {reason}")
    
    with open("reports.txt", 'a') as file:
        file.write(f"{user},{reason},{time}")

@bot.command(name="file")
async def file(ctx, file, exact = 0):

    global setup_done
    if not setup_done:
        await wakeup(ctx)
    
    if(exact > 0):
        try:
            await ctx.send(file = discord.File(file))
        except FileNotFoundError:
            await ctx.send("There are no such files currently")
        return

    if(file == "progress.txt" or file == "progress"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File("progress.txt"))

    elif(file == "reports.txt" or file == "reports"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File("reports.txt"))

    elif(file == "meeting.txt" or file == "meeting"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File("meeting.txt"))
    
    elif(file == "setup" or file == f"setup_{info.server_name}.txt"):
        await ctx.send(f"Here is the {file} file: ", file = discord.File(f"setup_{info.server_name}.txt"))

    elif(file == "todo"):

        await ctx.send("Here are your todo files: ")
        for filename in os.listdir("."):
            if filename.startswith("todo"):
                try:
                    await ctx.send(file = discord.File(filename))
                except ValueError:
                    await ctx.send("There are no todo files currently")

    elif(file == "workday"):
        await ctx.send("Here are your workday files: ")
        for filename in os.listdir("."):
            if filename.startswith("workday"):
                try:
                    await ctx.send(file = discord.File(filename))
                except ValueError:
                    await ctx.send("There are no workday files currently")

    elif(file == "all"):
        await ctx.send("Here are all your files: ")
        for filename in os.listdir("."):
            if filename.endswith(".txt"):
                await ctx.send(file = discord.File(filename))
    
    else:
        await ctx.send("There are no such files currently")

@bot.command("workday")
async def workday(ctx, user: discord.User):
    daily = []
    weekly = []
    end_of_week = []

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    await ctx.send(f"Collecting tasks for {user}. When you're done sending tasks, send 'send'")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    while True:
        msg = await bot.wait_for('message', check = check)

        if(msg.content.strip().lower() == 'send'):
            if(not daily and not weekly and not end_of_week):
                await ctx.send("Please send some tasks first")
            else:
                await ctx.send(f"Sending tasks to {user}")
                break

        match = re.match(r"\d \d+ (.+)", msg.content)

        if not match:
            await ctx.send("Incorrect message format. The format is: <deadline: 1 -> week, 0 -> day> <task number: 0 -> new task, anything else -> existing todo task> <task>")
            continue

        deadline = msg.content.split()[0]

        try:
            if(int(deadline) == 1):
                weekly.append(msg.content)
            elif(int(deadline) == 0):
                daily.append(msg.content)
            elif(int(deadline) == 2):
                end_of_week.append(msg.content)
            else:
                await ctx.send("The format is: <deadline: 1 -> week, 0 -> day> <task number: 0 -> new task, anything else -> existing todo task> <task>")
        except ValueError:
            await ctx.send("The format is: <deadline: 1 -> week, 0 -> day> <task number: 0 -> new task, anything else -> existing todo task> <task>")

    await send(user, daily, weekly, end_of_week)

async def send(user, daily, weekly, end_of_week):

    filename = f"workday_{user}.txt"
    with open(filename, 'a') as file:
        deadline = datetime.now() + timedelta(days=1)
        deadline = deadline.strftime("%d.%m.%y.")
        for entry in daily:
            file.write(f"Deadline,{deadline},")
            if(int(entry.split()[1]) == 0):
                info.index += 1
                task_number = info.index
            else:
                task_number = entry.split()[1]

            match = re.match(r"\d \d+ (.+)", entry)
            if match:
                result = match.group(1)

            file.write(f"{task_number},{result}\n")

        deadline = datetime.now() + timedelta(weeks=1)
        deadline = deadline.strftime("%d.%m.%y.")
        for entry in weekly:
            file.write(f"Deadline,{deadline},")
            if(int(entry.split()[1]) == 0):
                info.index += 1
                task_number = info.index
            else:
                task_number = entry.split()[1]

            match = re.match(r"\d \d+ (.+)", entry)
            if match:
                result = match.group(1)

            file.write(f"{task_number},{result}\n")

        today = datetime.now()
        days_to_friday = (4 - today.weekday()) % 7
        deadline = today + timedelta(days=days_to_friday)
        deadline = deadline.strftime("%d.%m.%y.")
        for entry in end_of_week:
            file.write(f"Deadline,{deadline},")
            if(int(entry.split()[1]) == 0):
                info.index += 1
                task_number = info.index
            else:
                task_number = entry.split()[1]

            match = re.match(r"\d \d+ (.+)", entry)
            if match:
                result = match.group(1)

            file.write(f"{task_number},{result}\n")

    await user.send("Here are your tasks: ", file=discord.File(filename))

    lines = None
    with open(f"setup_{info.server_name}.txt", "r") as file:
        lines = file.readlines()
    
    lines[-1] = f"index:{info.index}"
    with open(f"setup_{info.server_name}.txt", "w") as file:
        file.writelines(lines)

@bot.command(name="poll")
async def poll(ctx, *, content: str):
    
    import re
    matches = re.findall(r'"(.*?)"', content)

    if len(matches) < 3:
        await ctx.send("You need to provide a question and at least two options. Format:\n"
                       '`$poll "Your question?" "Option 1" "Option 2" ...`')
        return

    question = matches[0]
    options = matches[1:]

    if len(options) > 10:
        await ctx.send("You can only have up to 10 options.")
        return

    emoji_list = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
    description = "\n".join(f"{emoji_list[i]} {option}" for i, option in enumerate(options))

    embed = discord.Embed(title=f"📊 {question}", description=description, color=discord.Color.blurple())
    poll_msg = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_msg.add_reaction(emoji_list[i])

@bot.command(name="delay")
async def delay(ctx, id, *, message):

    global setup_done
    if not setup_done:
        await wakeup(ctx)

    feliname = f"workday_{ctx.author}.txt"
    lines = None
    with open(feliname, 'r') as file:
        lines = file.readlines()
    
    flag = 0
    for line in lines:
        if(line.split(",")[2] == id):
            flag = 1
            break

    if(not flag):
        await ctx.send("This task was not assigned to you")
        return

    filename = f"delay_{ctx.author}.txt"
    with open(filename, 'a') as file:
        file.write(f"{id},{message}\n")

    await ctx.send("Delay noted")

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
    filename = "todo_" + str(date.today()) + ".txt"
    try:
        await owner.send("Here's your todo file for today: ", file = discord.File(filename))
        print(f"File sent to {owner.name} (server owner).")
    except Exception as e:
        print(f"Failed to send file to the server owner: {e}")

bot.run(TOKEN)