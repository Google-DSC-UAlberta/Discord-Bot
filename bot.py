import os
from tabnanny import check

# https://discordpy.readthedocs.io/en/stable/api.html#
import discord
from discord.ext import tasks

import time
import asyncio
import json
import random
from dotenv import load_dotenv
from Database import Database

# load the envionment variables from .env file
load_dotenv()

TOKEN = os.getenv("API_TOKEN")

class GDSCJobClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.valid_messages = {
            "test": "Welcome to UofA GDSC!",
            "code": "```python\n print('showing how python snippets can be displayed on Discord!')```"
        }

        with open('greetings.json', 'r') as f:
            global greetings
            greetings = json.load(f)
        self.db = Database()
        self.tasks = {}
        

    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    
    async def notification(self, message):
        keywords_location = self.db.get_keywords_and_location(message.author.id)
        jobs = self.db.get_jobs(keywords_location['job_keywords'], keywords_location['location'])

        #there is a 4000 message limit
        limit = 10
        counter = 0
        for job in jobs:
            if counter < limit:
                embedVar = discord.Embed(title=job[0], url=job[3], color=0x00ff00)
                embedVar.add_field(name="Company", value=job[1], inline=False)
                embedVar.add_field(name="Location", value=job[2], inline=False)
                await message.reply(embed=embedVar)
                counter +=1
    
    def task_launcher(self, message, **interval):
        new_task = tasks.loop(**interval)(self.notification)
        self.tasks[message.author.id] = new_task
        new_task.start(message)
    
    async def manage_notification(self, message):
        if self.db.check_if_user_exist(message.author.id):      
            interval = self.db.get_notify_interval(message.author.id) # in minutes
            if message.author.id in self.tasks:
                await message.reply(f"Hi {message.author.name}, You will stop being notified for job postings!")
                self.tasks[message.author.id].cancel()
            else:
                self.task_launcher(message, minutes=interval)
                await message.reply(f"Hi {message.author.name}, you will start being notified for new job postings every {interval} minutes!")
        else:
            await message.reply(f"You haven't registered your job keywords and location yet. Please see the registration details")
            embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore. \
                                        \nAs for the notification interval, you can be choose to be notified every x amount of week(s)/day(s)/hour(s)/minute(s)", color=0x00ff00)
            embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
            await message.channel.send(embed=embedVar)

    async def on_message(self, message):
        #self.db.add_user(1234567890, 2, ["software"], ["Edmonton"])
        # a bot message also count as a message, make sure we don't handle bot's messages
        if message.author == self.user:
            return 

        content = message.content
        if content in self.valid_messages:
            await message.reply(self.valid_messages[content])
        elif content.lower() == "!notify":
            await self.manage_notification(message)
        elif content.lower() == "hello" or content.lower() == "hi":
            await message.reply(random.choices(greetings['Hello'])[0])
        elif content.lower() == "bye" or content.lower() == "goodbye": 
            await message.reply(random.choices(greetings['Bye'])[0])

        elif content.lower() == "!help":
            await message.reply("Hi, I am GDSC Job Bot!\n" + "I can help you with job postings!\n" +
            "Type '!register' to view the registration details and/or register\n" +
            "Type '!jobs' to see all the jobs I have based on your preferences\n" +
            "Type '!notify' to manage notification settings\n" +
            "Type '!help' to see this message again!")

        elif "how are you" in content.lower():
            await message.reply(random.choices(greetings['How are you'])[0])

        elif content == "!db":
            await message.reply(self.db.check_if_user_exist(message.author.id))

        elif content.lower() == "!jobs":
            if self.db.check_if_user_exist(message.author.id):
                keywords_location = self.db.get_keywords_and_location(message.author.id)
                jobs = self.db.get_jobs(keywords_location['job_keywords'], keywords_location['location'])

                #there is a 4000 message limit
                limit = 10
                counter = 0
                for job in jobs:
                    if counter < limit:
                        embedVar = discord.Embed(title=job[0], url=job[3], color=0x00ff00)
                        embedVar.add_field(name="Company", value=job[1], inline=False)
                        embedVar.add_field(name="Location", value=job[2], inline=False)
                        await message.reply(embed=embedVar)
                        counter +=1
                
            else:
                await message.reply(f"You haven't registered your job keywords and location yet. Please see the registration details")
                embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                await message.channel.send(embed=embedVar)

        elif "!register" in content.lower():

            if (content.count('/') != 2):
                await message.reply("You must use exactly two '/'. Please try again")
                embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                await message.channel.send(embed=embedVar)
            else:
                content = content.replace("!register", "", 1) # Remove "!register"
                result = content.split('/') # Split them by "/"
                result = [x.strip() for x in result] # Remove unnecessary whitespace
                user_jobs = result[0].split() # Split the job keyword(s) by whitespaces
                user_jobs_results = []
                for user_job in user_jobs:
                    user_jobs_results.append(user_job.replace("_", " "))

                user_locations = result[1].split() # Split the locations by whitespaces
                user_locations_results = [] 
                for user_location in user_locations:
                    user_locations_results.append(user_location.replace("_", " "))
                
                if (result[2][-1] not in ('w', 'd', 'h', 'm')): # The user doesn't select one of the available options
                    await message.reply("Error while parsing the notify_interval. Please try again and make sure it is in the correct format.")
                else: # Convert the time interval into minutes
                    if (result[2][-1] == 'w'):
                        user_notify_interval = int(result[2].split('w')[0]) * 10080
                    elif (result[2][-1] == 'd'):
                        user_notify_interval = int(result[2].split('d')[0]) * 1440
                    elif (result[2][-1] == 'h'):
                        user_notify_interval = int(result[2].split('h')[0]) * 60
                    elif (result[2][-1] == 'm'):
                        user_notify_interval = int(result[2].split('m')[0])

                self.db.add_user(message.author.id, user_notify_interval, user_jobs_results, user_locations_results) # Write to the db

                if self.db.check_if_user_exist(message.author.id):
                    # Turn each list into a string and display it to the user
                    user_jobs_string = ", ".join(user_jobs_results)
                    user_locations_string = ", ".join(user_locations_results)

                    embedVar = discord.Embed(title="Registration Successful!", color=0x00ff00)
                    embedVar.add_field(name="Job Keyword(s)", value=user_jobs_string, inline=False)
                    embedVar.add_field(name="Location(s)", value=user_locations_string, inline=False)
                    embedVar.add_field(name="Notify Interval (in minutes)", value=user_notify_interval, inline=False)
                    await message.channel.send(embed=embedVar)
                else:
                    await message.reply("Registration unsucccessful. Please try again.")

client = GDSCJobClient()
client.run(TOKEN)