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
        #use whichever command works with your laptop
        with open('greetings.json', 'r') as f:
            global greetings
            greetings = json.load(f)
        self.db = Database()
        self.tasks = {}
        

    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    
    async def notification(self, message):
        # TODO: replace with actual job posting
        await message.reply("Hello World!")
    
    def task_launcher(self, message, **interval):
        new_task = tasks.loop(**interval)(self.notification)
        self.tasks[message.author.id] = new_task
        new_task.start(message)
    
    async def manage_notification(self, message):
        # TODO: retrieve interval from database based on message.author.id
        interval = 1 # in minutes
        if message.author.id in self.tasks:
            await message.reply(f"Hi {message.author.name}, You will stop being notified for job postings!")
            self.tasks[message.author.id].cancel()
        else:
            self.task_launcher(message, minutes=interval)
            await message.reply(f"Hi {message.author.name}, you will start being notified for new job postings every {interval} minutes!")

    async def on_message(self, message):
        #self.db.add_user(1234567890, 2, ["software"], ["Edmonton"])
        # a bot message also count as a message, make sure we don't handle bot's messages
        if message.author == self.user:
            return 

        content = message.content
        if content in self.valid_messages:
            await message.reply(self.valid_messages[content])
        elif content.lower() == "notify":
            await self.manage_notification(message)
        elif content.lower() == "hello" or content.lower() == "hi":
            await message.reply(random.choices(greetings['Hello'])[0])
        elif content.lower() == "bye" or content.lower() == "goodbye": 
            await message.reply(random.choices(greetings['Bye'])[0])

        elif content.lower() == "help":
            await message.reply("Hi, I am GDSC Job Bot!\n" + "I can help you with job postings!\n" +
            "Type 'register' to view the registration details\n" +
            "Type 'jobs' to see all the jobs I have based on your preferences\n" +
            "Type 'notify' to manage notification settings\n" +
            "Type 'help' to see this message again!")

        elif "how are you" in content.lower():
            await message.reply(random.choices(greetings['How are you'])[0])

        elif content == "db":
            await message.reply(self.db.check_if_user_exist(message.author.id))

        elif content == "register":
            embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!jobs Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
            embedVar.add_field(name="Examples", value="`!jobs Software_Engineer / Edmonton Toronto Los_Angeles/ 60\n\n!jobs Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 120`", inline=False)
            await message.channel.send(embed=embedVar)

        elif content.lower() == "jobs":
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
                embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!jobs Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                embedVar.add_field(name="Examples", value="`!jobs Software_Engineer / Edmonton Toronto Los_Angeles/ 60\n\n!jobs Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 120`", inline=False)
                await message.channel.send(embed=embedVar)

        elif "!jobs" in content.lower():
            if (content.count('/') != 2):
                await message.reply("You must use exactly two '/'. Please try again")
            else:
                content = content.replace("!jobs", "", 1) # Remove "!jobs"
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

                user_notify_interval = int(result[2])
                
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
