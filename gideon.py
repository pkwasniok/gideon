# Imports
from dotenv import load_dotenv
import discord
import asyncio
import json
from datetime import datetime
import os

DIR = "C://repos/Projects/Gideon"

# Credentials
load_dotenv(DIR + "/.env")
TOKEN = os.getenv("TOKEN")

# Variables
lesson = -1
break_number = -1
days = []
lessons = []
lessons_hours = []
day = 0
hours = 0
minutes = 0
time = 0
day_status = "weekend"

# Loadin json file
with open(DIR + "/config.json", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Loading timetable from json file
for i in range(len(data["timetable"])):
    days.append(data["timetable"][i]["day"])
    lessons.append([])
    for j in range(len(data["timetable"][i]["lessons"])):
        lessons[i].append(data["timetable"][i]["lessons"][j])

# Loading hours from json file
lessons_hours = data["hours"]

# Loading lesson duration from json file
lesson_duration = data["lesson_duration"]

# Creating client
client = discord.Client()

# Bot settings
BOT_SYNTAX = data["syntax"]

# Function that updates all variables like lesson number and etc


def timeToMinutes(time):
    hours = int(time.split(":")[0])
    minutes = int(time.split(":")[1])
    return hours*60 + minutes

# ====Funkcja, która aktualizuje aktualny czas (nr lekcji, dzień tygodnia, itp)====


def updateTime():
    global day, hours, minutes, time, lesson, break_number, day_status
    day = (int(datetime.now().strftime('%d')) % len(days))-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes
    lesson = -1

    for i in range(len(lessons[day])):
        if(time >= timeToMinutes(lessons_hours[i]) and time <= (timeToMinutes(lessons_hours[i])+lesson_duration)):
            lesson = i

    for i in range(len(lessons[day])-1):
        if((time > timeToMinutes(lessons_hours[i])+lesson_duration) and (time < timeToMinutes(lessons_hours[i+1]))):
            break_number = i

    if(len(lessons[day]) == 0):
        day_status = "weekend"
    elif(lesson == -1):
        day_status = "break"
    else:
        day_status = "lesson"


@client.event
async def on_ready():
    for guild in client.guilds:
        print(guild.name)
    print("User:", client.user, "Name: ", guild.name, "Id:", guild.id)


@client.event
async def on_message(message):
    updateTime()  # Updating variables
    channel = message.channel  # Reading messages

    # Updating status
    activity = data["statuses"][day_status]["text"].replace(
        "{lesson}", lessons[day][lesson])
    activity = activity.replace("{next-lesson}", lessons[day][lesson+1])
    if(data["statuses"][day_status]["status"] == "online"):
        status = discord.Status.online
    else:
        status = discord.Status.idle
    await client.change_presence(status=status, activity=discord.Game(activity))

    if(message.content.startswith(BOT_SYNTAX)):
        if(message.content.find(" ") == -1):
            command = message.content.split(" ")[0][1:]

            # ====plan====
            if(command == "plan"):
                reponse = ":calendar: `" + days[day] + "`\n"
                for i in range(len(lessons[day])):
                    if (lessons[day][i] != ""):
                        reponse += ":clock1: `" + lessons_hours[i] + \
                            " - " + str((timeToMinutes(lessons_hours[i])+lesson_duration)//60).zfill(2) + \
                            ":" + str((timeToMinutes(lessons_hours[i])+lesson_duration) % 60).zfill(2) + "` ▫ `" + \
                            lessons[day][i] + "`\n"
                await message.channel.send(reponse)

            # ====ilelekcji====
            if(command == "ilelekcji" or command == "il"):
                if(lesson == -1):
                    time_to_end = timeToMinutes(
                        lessons_hours[break_number])-time
                    response = "Do końca lekcji zostało `" + \
                        str(time_to_end) + "` minut"
                    await message.channel.send(response)
                else:
                    lesson_end = timeToMinutes(lessons_hours[lesson]) + 45
                    reponse = "`" + lessons[day][lesson] + \
                        "` kończy się o `" + \
                        str(lesson_end//60).zfill(2) + ":" + \
                        str(lesson_end % 60).zfill(2) + "`\n" + \
                        "Zostało `" + str(lesson_end-time) + \
                        "` minut do końca lekcji"
                    await message.channel.send(reponse)

            # ====ileczasu====
            if(command == "ileczasu" or command == "ic"):
                lesson_end = timeToMinutes(
                    lessons_hours[len(lessons[day])-1]) + 45
                response = "Do końca zostało `" + \
                    str(len(lessons[day])-lesson) + "` lekcji\n"
                response += "czyli `" + \
                    str((lesson_end-time)//60) + "` h i `" + \
                    str((lesson_end-time) % 60) + "` min"
                await message.channel.send(response)

            # ====help====
            if(command == "help"):
                response = ":question: **Help** :question:\n"
                response += "`" + data["syntax"] + \
                    "timetable` ▫ sends the timetable\n"
                response += "`" + data["syntax"] + "timeuntilend` or `" + data["syntax"] + \
                    "tud` ▫ sends the remaining time of the lesson"
                await message.channel.send(response)

# Running bot with TOKEN
client.run(TOKEN)
