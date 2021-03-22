# Imports
from dotenv import load_dotenv
import discord
import asyncio
from discord.ext import tasks
import json
from datetime import datetime
import os

# Bot working directory
DIR = "C://repos/Projects/Gideon"

# Loading bot token from .env file
load_dotenv(DIR + "/.env")
TOKEN = os.getenv("TOKEN")

# Variables
lesson = -1
break_number = -1
days = []
lessons = []
links = []
lessons_hours = []
day = 0
hours = 0
minutes = 0
time = 0
day_status = "weekend"

# Loading json file
with open(DIR + "/config.json", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Loading timetable from json file
for i in range(len(data["timetable"])):
    days.append(data["timetable"][i]["day"])
    lessons.append([])
    for j in data["timetable"][i]["lessons"]:
        if(j.find("{") != -1 and j.find("}") != -1):
            lessons[i].append(j[:j.find("{")])
        else:
            lessons[i].append(j)


# Loading meet links from json file
for i in range(len(data["timetable"])):
    links.append([])
    for j in data["timetable"][i]["lessons"]:
        if(j.find("{") != -1 and j.find("}") != -1):
            links[i].append(j[j.find("{")+1:j.find("}")])
        else:
            links[i].append("")

# Loading hours from json file
lessons_hours = data["hours"]

# Loading lesson duration from json file
lesson_duration = data["lesson_duration"]

# Creating client object
client = discord.Client()

# Setting bot syntax (from config.json)
BOT_SYNTAX = data["syntax"]

# Loading events from events.json
with open(DIR + "/events.json", encoding="utf-8") as json_file:
    events = json.load(json_file)


def lessonToIndex(lesson):  # unkcja konwertująca nazwę lekcji na numer(index) lekcji
    i = -1
    for j in range(len(lessons[day])):
        if(lesson.lower() == lessons[day][j].lower()):
            i = j
            break
    return i


def timeToMinutes(time):  # Funkcja konwertująca czas z formatu "HH:MM" na minuty np 1:30 -> 90
    hours = int(time.split(":")[0])
    minutes = int(time.split(":")[1])
    return hours*60 + minutes


async def updateTime():  # Funkajc aktualizująca czas, numer] lekcji, itp.
    global day, hours, minutes, time, lesson, break_number, day_status
    day = (int(datetime.now().strftime('%d')) % (len(days)))-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes
    lesson = -1

    for i in range(len(lessons[day])-1):
        if(time >= timeToMinutes(lessons_hours[i]) and time < (timeToMinutes(lessons_hours[i])+lesson_duration)):
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

    # Updating status
    activity = data["statuses"][day_status]["text"].replace(
        "{lesson}", lessons[day][lesson])
    activity = activity.replace(
        "{next-lesson}", lessons[day][break_number+1])
    activity = activity.replace(
        "{time-until-lesson-end}", str(timeToMinutes(lessons_hours[lesson]) + 45 - time))
    if(data["statuses"][day_status]["status"] == "online"):
        status = discord.Status.online
    else:
        status = discord.Status.idle
    await client.change_presence(status=status, activity=discord.Game(activity))


@ tasks.loop(seconds=20)
async def sync():  # Pętal w której uakualniany jest czas, lekcja, wysyłane są powiadomienia
    await updateTime()
    channel = client.get_channel(data["info-channel-id"])
    # await channel.send("Siema")


@ client.event
async def on_ready():  # Po dołączeniu na serwer (włączeniu bota)
    for guild in client.guilds:
        print(guild.name)
    print("User:", client.user, "Name: ", guild.name, "Id:", guild.id)
    sync.start()


@ client.event
async def on_message(message):
    await updateTime()  # Updating variables
    channel = message.channel  # Reading messages

    if(message.content.startswith(BOT_SYNTAX)):
        if(message.content.find(" ") == -1):
            # Extracting command from message
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
                if(len(lessons[day]) == 0):
                    response += ":tada: Dzisiaj nie ma lekcji :tada:"
                await message.channel.send(reponse)

            # ====planjutro====
            if(command == "planjutro"):
                reponse = ":calendar: `" + days[day+1] + "`\n"
                for i in range(len(lessons[day+1])):
                    if (lessons[day+1][i] != ""):
                        reponse += ":clock1: `" + lessons_hours[i] + \
                            " - " + str((timeToMinutes(lessons_hours[i])+lesson_duration)//60).zfill(2) + \
                            ":" + str((timeToMinutes(lessons_hours[i])+lesson_duration) % 60).zfill(2) + "` ▫ `" + \
                            lessons[day+1][i] + "`\n"
                await message.channel.send(reponse)

            # ====ilelekcji====
            if(command == "ilelekcji" or command == "il"):
                if(lesson == -1 and break_number == -1):
                    await message.channel.send(":tada: Dzisiaj nie ma już lekcji :tada:")
                elif(lesson == -1):
                    time_to_end = timeToMinutes(
                        lessons_hours[break_number+1])-time
                    response = "Do końca przerwy zostało `" + \
                        str(time_to_end) + "` minut"
                    await message.channel.send(response)
                else:
                    lesson_end = timeToMinutes(lessons_hours[lesson]) + 45
                    reponse = "`" + lessons[day][lesson] + "` kończy się o `" + \
                        str(lesson_end//60).zfill(2) + ":" + \
                        str(lesson_end % 60).zfill(2) + "`\n" + \
                        "Zostało `" + str(lesson_end-time) + \
                        "` minut do końca lekcji"
                    await message.channel.send(reponse)

            # ====ileczasu====
            if(command == "ileczasu" or command == "ic"):
                if(lesson == -1 and break_number == -1):
                    await message.channel.send(":tada: Lekcje się już skończyły :tada:")
                else:
                    lesson_end = timeToMinutes(
                        lessons_hours[len(lessons[day])-1]) + 45
                    response = "Do końca zostało `" + \
                        str(len(
                            lessons[day]) - (break_number if lesson == -1 else lesson)) + "` lekcji\n"
                    response += "czyli `" + \
                        str((lesson_end-time)//60) + "` h i `" + \
                        str((lesson_end-time) % 60) + "` min"
                    await message.channel.send(response)

            # ====meet====
            if(command == "meet"):
                if(links[day][lesson] != ""):
                    desc = "[" + links[day][lesson] + \
                        "](https://meet.google.com/" + \
                        links[day][lesson] + ")"
                else:
                    desc = "Nie zdefiniowano linku dla tej lekcji :frowning:"
                embed = discord.Embed(
                    title=lessons[day][lesson], description=desc, color=0x00ff00)
                await message.channel.send(embed=embed)

            # ====pomoc====
            if(command == "pomoc"):
                embed = discord.Embed(
                    title=":question: Pomoc :question:", color=0xff0000)
                embed.add_field(
                    name=BOT_SYNTAX+"plan <dzień>", value="Wyświetla plan na dzisiaj lub na podany dzień", inline=False)
                embed.add_field(name=BOT_SYNTAX+"planjutro",
                                value="Wyświetla plan na jutro", inline=False)
                embed.add_field(
                    name=BOT_SYNTAX+"ilelekcji | " + BOT_SYNTAX+"il", value="Wyświetla czas pozostały do końca aktualnej lekcji/przerwy", inline=False)
                embed.add_field(
                    name=BOT_SYNTAX+"ileczasu | " + BOT_SYNTAX+"ic", value="Wyświetla czas pozostały do końca wszystkich lekcji", inline=False)
                embed.add_field(
                    name=BOT_SYNTAX+"dodaj <nazwa> <godzina> <data> <przypomnienie> <przedmiot> <\"opis\">", value="Dodaje nowe wydarzenie", inline=False)
                await message.channel.send(embed=embed)

            # ====wydarzenia====
            if(command == "wydarzenia"):
                embed = discord.Embed(
                    title="Nadchodzące wydarzenia", color=0x0000ff)

                for i in range(len(events['events'])):
                    desc = "Godzina: " + events['events'][i]['time'] + "\n" + \
                        "Data: " + events['events'][i]['date'] + "\n" + \
                        "Przypomnienie: " + events['events'][i]['reminder'] + "\n" + \
                        "Przedmiot: " + events['events'][i]['subject'] + "\n" + \
                        "Opis: " + events['events'][i]['description']
                    embed.add_field(
                        name=events['events'][i]['name'], value=desc, inline=False)

                await message.channel.send(embed=embed)
        else:
            # Extracting command and args from message
            command = message.content.split(" ")[0][1:]
            args = message.content.split(" ")[1:]

            # ====plan-day====
            if(command == "plan" and (len(args) == 1 or len(args) == 2)):
                arg_num = 0
                if(args[0].lower() == 'na'):
                    arg_num = 1

                day_number = -1
                for day_number in range(len(data["timetable"])):
                    if(data["timetable"][day_number]["day"][:-1].lower() == args[arg_num][:-1].lower()):
                        break
                if(args[arg_num].lower() == "jutro"):
                    day_number = day+1
                if(day_number != -1):
                    response = ":calendar: `" + days[day_number] + "`\n"
                    for i in range(len(lessons[day_number])):
                        if (lessons[day_number][i] != ""):
                            response += ":clock1: `" + lessons_hours[i] + \
                                " - " + str((timeToMinutes(lessons_hours[i])+lesson_duration)//60).zfill(2) + \
                                ":" + str((timeToMinutes(lessons_hours[i])+lesson_duration) % 60).zfill(2) + "` ▫ `" + \
                                lessons[day_number][i] + "`\n"
                    if(len(lessons[day_number]) == 0):
                        response += ":tada: Dzisiaj nie ma lekcji :tada:"
                    await message.channel.send(response)

            # ====meet-day====
            if(command == "meet" and len(args) == 1):
                if(lessonToIndex(args[0]) == -1):
                    await message.channel.send("Dzisiaj nie ma takiej lekcji")
                else:
                    if(links[day][lessonToIndex(args[0])] != ""):
                        desc = "[" + links[day][lessonToIndex(args[0])] + \
                            "](https://meet.google.com/" + \
                            links[day][lessonToIndex(args[0])] + ")"
                    else:
                        desc = "Nie zdefiniowano linku dla tej lekcji :frowning:"
                    embed = discord.Embed(
                        title=lessons[day][lessonToIndex(args[0])], description=desc, color=0x00ff00)
                    await message.channel.send(embed=embed)

            # ====doda-event====
            if(command == "dodaj"):
                # getting desc from message
                desc = message.content.split("\"")[1]

                dict = {
                    "name": args[0],
                    "time": args[1],
                    "date": args[2],
                    "reminder": args[3],
                    "subject": args[4],
                    "description": desc
                }

                events['events'].append(dict)

                with open(DIR + "/events.json", "r+", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                    data.update(events)
                    json_file.seek(0)
                    json.dump(events, json_file)

                await message.channel.send("Dodano wydarzenie " + events['events'][len(events['events'])-1]['name'])

# Running bot with TOKEN
client.run(TOKEN)
