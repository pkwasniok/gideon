# Imports
from dotenv import load_dotenv
import discord
import asyncio
import json
from datetime import datetime
import os

DIR = "C://repos/Gideon"

# Credentials
load_dotenv(DIR + "/.env")
TOKEN = os.getenv("TOKEN")

# Variables
lesson = -1
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


def updateTime():
    global day, hours, minutes, time, lesson
    day = (int(datetime.now().strftime('%d')) % len(days))-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes
    lesson = -1

    day = 0

    for i in range(len(lessons[day])):
        if(time > timeToMinutes(lessons_hours[i]) and time < (timeToMinutes(lessons_hours[i])+lesson_duration)):
            lesson = i

    lesson = 1

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
    activity = activity.replace("{next-lesson}", lessons[day][lesson])
    if(data["statuses"][day_status]["status"] == "online"):
        status = discord.Status.online
    else:
        status = discord.Status.idle
    await client.change_presence(status=status, activity=discord.Game(activity))

    if(message.content.startswith(BOT_SYNTAX)):
        if(message.content.find(" ") == -1):
            command = message.content.split(" ")[0][1:]

            if(command == "timetable"):
                reponse = ":calendar: `" + days[day] + "`\n"
                for i in range(len(lessons[day])):
                    reponse += ":clock1: `" + lessons_hours[i] + \
                        " - " + str((timeToMinutes(lessons_hours[i])+lesson_duration)//60) + \
                        ":" + str((timeToMinutes(lessons_hours[i])+lesson_duration) % 60).zfill(2) + "` ▫ `" + \
                        lessons[day][i] + "`\n"
                await message.channel.send(reponse)

            if(command == "timeuntilend" or command == "tud"):
                lesson_end = timeToMinutes(lessons_hours[lesson]) + 45
                reponse = "`" + lessons[day][lesson] + \
                    "` kończy się o `" + \
                    str(lesson_end//60) + ":" + \
                    str(lesson_end % 60).zfill(2) + "`\n" + \
                    "Zostało `" + str(lesson_end-time) + \
                    "`minut do końca lekcji"
                await message.channel.send(reponse)

            if(command == "time"):
                response = str(day) + "\n" + str(lesson) + \
                    "\n" + lessons[day][lesson]
                await message.channel.send(response)

            if(command == "help"):
                response = ":question: **Help** :question:\n"
                response += "`" + data["syntax"] + \
                    "timetable` ▫ sends the timetable\n"
                response += "`" + data["syntax"] + "timeuntilend` or `" + data["syntax"] + \
                    "tud` ▫ sends the remaining time of the lesson"
                await message.channel.send(response)

# Running bot with TOKEN
client.run(TOKEN)

'''
import os

import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot

from datetime import datetime

import asyncio

from urllib.request import urlopen
url = "https://www.zsijp.pl/zastepstwa/"

dzien = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']

# Rozpiska lekcji w miutach
# 460 - 525 --- 1 lekcja
# 525 - 530 --- przerwa
# 530 - 575 --- 2 lekcja
# 575 - 580 --- przerwa
# 580 - 625 --- 3 lekcja
# 625 - 640 --- przerwa
# 640 - 685 --- 4 lekcja
# 685 - 690 --- przerwa
# 690 - 735 --- 5 lekcja
# 735 - 750 --- przerwa
# 750 - 795 --- 6 lekcja
# 795 - 800 --- przerwa
# 800 - 845 --- 7 lekcja
# 845 - 850 --- przerwa
# 850 - 895 --- 8 lekcja

lekcje = [['Matematyka', 'Matematyka', 'Filozofia', 'WOS', 'Polski', 'Polski', 'Religia', 'Niemiecki'],
          ['', 'Polski', 'Edb', 'Historia', 'Matematyka',
              'Angielski', 'Angielski', 'Informatyka'],
          ['Angielski', 'Matematyka', 'Historia', 'Geografia',
              'Fizyka/Biologia', 'Religia', 'Programowanie'],
          ['Matematyka', 'Niemiecki', 'Wychowawcza',
              'Biologia/Fizyka', 'Wf', 'Wf', 'Polski', 'Informatyka'],
          ['Angielski', 'Wf', 'Chemia', 'Fizyka/Biologia', 'Angielski']]

godziny = ['8:00 - 8:45', '8:50 - 9:35', '9:40 - 10:25', '10:40 - 11:25',
           '11:30 - 12:15', '12:30 - 13:15', '13:20 - 14:05', '14:10 - 14:55']

client = discord.Client()
bot = commands.Bot(command_prefix='.', description='Elo')


@bot.command(name='pomoc')
async def pomoc(ctx):
    await ctx.send("`.data` - wyświetla aktualną datę \n`.konieclekcji` - wyświetla godzinę o któej kończą się lekcje \n`.lekcja` - wyświetla aktualną oraz następną lekcję \n`.plan` - wyświetla plan lekcji na dzisiaj \n`.ileczasu` - wyświetla czas pozostały do zakończenia wszystkich lekcji \n`.ilelekcji` - wyświetla czas pozostały do zakończenia aktualnej lekcji")


@bot.command(name='zastepstwa')
async def zastepstwa(ctx):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    fragment = html[html.find("<em>"): html.find("</em>")]
    await ctx.send(fragment[12: html.find("</strong>")])


@ bot.command(name='data')
async def data(ctx):
    await ctx.send(datetime.now().strftime("%Y-%m-%d"))


@bot.command(name='ileczasu')
async def ileczasu(ctx):
    dzien = (int(datetime.now().strftime('%d')) % 7)-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes

    lekcja = -1

    if(time > 460 and time < 525):  # Lekcja 1
        lekcja = 0
    elif(time > 530 and time < 575):  # Lekcja 2
        lekcja = 1
    elif(time > 580 and time < 625):  # Lekcja 3
        lekcja = 2
    elif(time > 640 and time < 685):  # Lekcja 4
        lekcja = 3
    elif(time > 690 and time < 720):  # Lekcja 5
        lekcja = 4
    elif(time > 750 and time < 795):  # Lekcja 6
        lekcja = 5
    elif(time > 800 and time < 845):  # Lekcja 7
        lekcja = 6
    elif(time > 850 and time < 895):  # Lekcja 8
        lekcja = 7

    ile_lekcji = (len(lekcje[dzien])-lekcja)

    ile_minut = (int(godziny[len(lekcje[dzien])-1].split(" - ")[1].split(":")[0])
                 * 60 + int(godziny[len(lekcje[dzien])-1].split(" - ")[1].split(":")[1])) - time

    if(ile_lekcji == 1):
        await ctx.send("Jeszcze tylko jedna lekcja! :tada:")
    else:
        await ctx.send("Zostało jeszcze `" + str(ile_lekcji) + "` lekcji, czyli `" + str(ile_minut//60) + "` h i `" + str(ile_minut % 60) + "` minut")


@bot.command(name='ilelekcji')
async def ilelekcji(ctx):
    dzien = (int(datetime.now().strftime('%d')) % 7)-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes

    lekcja = -1

    if(time > 460 and time < 525):  # Lekcja 1
        lekcja = 0
    elif(time > 530 and time < 575):  # Lekcja 2
        lekcja = 1
    elif(time > 580 and time < 625):  # Lekcja 3
        lekcja = 2
    elif(time > 640 and time < 685):  # Lekcja 4
        lekcja = 3
    elif(time > 690 and time < 720):  # Lekcja 5
        lekcja = 4
    elif(time > 750 and time < 795):  # Lekcja 6
        lekcja = 5
    elif(time > 800 and time < 845):  # Lekcja 7
        lekcja = 6
    elif(time > 850 and time < 895):  # Lekcja 8
        lekcja = 7
    else:
        await ctx.send("Teraz jest przerwa :tada:")

    if(lekcja != -1):
        koniec = godziny[lekcja].split(" - ")
        minuty_str = koniec[1].split(":")
        minuty_aktualne_str = datetime.now().strftime("%H %M").split(" ")
        minuty_aktualne = int(
            minuty_aktualne_str[0])*60 + int(minuty_aktualne_str[1])
        minuty_koniec = int(minuty_str[0])*60 + int(minuty_str[1])
        koniec_godzina = godziny[lekcja].split(" - ")[1]

        if(lekcje[dzien][lekcja] == lekcje[dzien][lekcja+1]):
            minuty_koniec += 50
            koniec_godzina = godziny[lekcja+1].split(" - ")[1]

        minuty_roznica = minuty_koniec - minuty_aktualne

        response = "`" + lekcje[dzien][lekcja] + "` kończy się o `" + koniec_godzina + \
            "`\nZostało `" + str(minuty_roznica) + "` minut do końca lekcji"
        await ctx.send(response)


@ bot.command(name='konieclekcji')
async def konieclekcji(ctx):
    dzien = (int(datetime.now().strftime('%d')) % 7)-1
    if(dzien == 2):
        koniec = "o godzinie `16:00`"
    elif (len(lekcje[dzien]) == 5):
        koniec = "o godzinie `12:15`"
    elif (len(lekcje[dzien]) == 6):
        koniec = "o godzinie `13:15`"
    elif (len(lekcje[dzien]) == 7):
        koniec = "o godzinie `14:05`"
    elif (len(lekcje[dzien]) == 8):
        koniec = "o godzinie `14:55`"
    else:
        koniec = "`za późno`"

    response = "Dzisiaj koniec lekcji jest " + koniec
    await ctx.send(response)


@ bot.command(name='plan')
async def plan(ctx):
    dzien = (int(datetime.now().strftime('%d')) % 7)-1
    response = " "
    for i in range(len(lekcje[dzien])):
        if(lekcje[dzien][i] != ""):
            response += str(i+1) + ". :clock1: `" + \
                godziny[i] + "` --> `" + lekcje[dzien][i] + "`\n"
    await ctx.send(response)


@ bot.command(name='lekcja')
async def lekcja(ctx):
    # odczytywanie aktualnej daty i godziny
    dzien = (int(datetime.now().strftime('%d')) % 7)-1
    hours = int(datetime.now().strftime('%H'))
    minutes = int(datetime.now().strftime('%M'))
    time = hours*60+minutes
    lekcja = 0

    # odczytywanie numery lekcji na podstawie minut dnia
    if(time > 460 and time < 525):  # Lekcja 1
        lekcja = 0
    elif(time > 530 and time < 575):  # Lekcja 2
        lekcja = 1
    elif(time > 580 and time < 625):  # Lekcja 3
        lekcja = 2
    elif(time > 640 and time < 685):  # Lekcja 4
        lekcja = 3
    elif(time > 690 and time < 720):  # Lekcja 5
        lekcja = 4
    elif(time > 750 and time < 795):  # Lekcja 6
        lekcja = 5
    elif(time > 800 and time < 845):  # Lekcja 7
        lekcja = 6
    elif(time > 850 and time < 895):  # Lekcja 8
        lekcja = 7

    if(lekcja+1 < len(lekcje[dzien])):
        response = "Aktualna lekcja: `" + \
            lekcje[dzien][lekcja] + "` \n" + \
            "Następna lekcja: `" + lekcje[dzien][(lekcja+1)] + "`"
    else:
        response = "Aktualna lekcja: `" + \
            lekcje[dzien][lekcja] + "` \n" + "Koniec lekcji byczki! :tada:"

    await ctx.send(response)


bot.run('ODE0MDI2NDQwNTEyMzcyNzQ2.YDX3Mw.qiVDz5n0leo-0TnVIcxZlSEH7OY')
'''
