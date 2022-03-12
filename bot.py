import os
import re
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
        self.counter = 0
        self.limit = 0
        

    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    
    async def notification(self, message):
        keywords_location = self.db.get_keywords_and_location(message.author.id)
        jobs = self.db.get_jobs(job_keywords=keywords_location['job_keywords'], locations=keywords_location['location'])

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

    async def parse_registration(self, content):
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
        
        if (result[2][-1] == 'w'):
            user_notify_interval = int(result[2].split('w')[0]) * 10080
        elif (result[2][-1] == 'd'):
            user_notify_interval = int(result[2].split('d')[0]) * 1440
        elif (result[2][-1] == 'h'):
            user_notify_interval = int(result[2].split('h')[0]) * 60
        elif (result[2][-1] == 'm'):
            user_notify_interval = int(result[2].split('m')[0])
        return {"user_jobs_results": user_jobs_results, "user_locations_results": user_locations_results, "user_notify_interval": user_notify_interval}

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
            "Type '!view' to view your current registation\n" +
            "Type '!modify' to modify your current registration\n" +
            "Type '!help' to see this message again!")

        elif "how are you" in content.lower():
            await message.reply(random.choices(greetings['How are you'])[0])

        elif content == "!db":
            await message.reply(self.db.check_if_user_exist(message.author.id))

        elif "!jobs" in content.lower():
            if (any(char.isdigit() for char in content) == False): 
                await message.reply("You must input a page number. Try '!jobs <page_number>'")
            else:
                pg_num = int(re.search(r'\d+', content).group()) #pg number
                if self.db.check_if_user_exist(message.author.id):
                    keywords_location = self.db.get_keywords_and_location(message.author.id)
                    jobs = self.db.get_jobs(keywords_location['job_keywords'], keywords_location['location'],pg_num)
                    
                    for job in jobs:
                        embedVar = discord.Embed(title=job[0], url=job[3], color=0x00ff00)
                        embedVar.add_field(name="Company", value=job[1], inline=False)
                        embedVar.add_field(name="Location", value=job[2], inline=False)
                        await message.reply(embed=embedVar)
                       
                else:
                    await message.reply(f"You haven't registered your job keywords and location yet. Please see the registration details")
                    embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                    embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                    await message.channel.send(embed=embedVar)


        elif "!register" in content.lower():
            if self.db.check_if_user_exist(message.author.id): # Check if the user has already registered
                await message.reply("You've already registered. Use `!view` to view your registration details and `!modify` to modify.")
            else:
                if (content.count('/') != 2):
                    await message.reply("You must use exactly two '/'. Please try again")
                    embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                    embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                    await message.channel.send(embed=embedVar)
                else:
                    content = content.replace("!register", "", 1) # Remove "!register"
                    if (content.split('/')[2][-1] not in ('w', 'd', 'h', 'm')): # The user doesn't select one of the available notify_interval units
                        await message.reply("Error while parsing the notify_interval. Please try again and make sure it is in the correct format.")
                    else:
                        results = await self.parse_registration(content)

                        self.db.add_user(message.author.id, results["user_notify_interval"], results["user_jobs_results"], results["user_locations_results"]) # Write to the db

                        if self.db.check_if_user_exist(message.author.id):
                            # Turn each list into a string and display it to the user
                            user_jobs_string = ", ".join(results["user_jobs_results"])
                            user_locations_string = ", ".join(results["user_locations_results"])

                            embedVar = discord.Embed(title="Registration Successful!", color=0x00ff00)
                            embedVar.add_field(name="Job Keyword(s)", value=user_jobs_string, inline=False)
                            embedVar.add_field(name="Location(s)", value=user_locations_string, inline=False)
                            embedVar.add_field(name="Notify Interval (in minutes)", value=results["user_notify_interval"], inline=False)
                            await message.channel.send(embed=embedVar)
                        else:
                            await message.reply("Registration unsucccessful. Please try again.")

        elif "!view" in content.lower():
            if self.db.check_if_user_exist(message.author.id): # Check if the user has already registered
                keywords_and_locations = self.db.get_keywords_and_location(message.author.id)
                embedVar = discord.Embed(title="View your current registration", description="Job keywords: `"+', '.join(keywords_and_locations["job_keywords"])+"`\nLocations: `"+', '.join(keywords_and_locations["location"])+"`\nNotify Interval: Every `"+str(self.db.get_notify_interval(message.author.id))+"` minutes" , color=0x00ff00)
                embedVar.add_field(name="To modify your registration, use `!modify`. (Note: Modifying your registration will replace your current registration). Examples:", value="`!modify Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!modify Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                await message.channel.send(embed=embedVar)

            else:
                await message.reply("You must first register before you can view your registration")
                embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                await message.channel.send(embed=embedVar)

        elif "!modify" in content.lower():
            if self.db.check_if_user_exist(message.author.id): # Check if the user has already registered
                if (content.count('/') != 2):
                    await message.reply("You must use exactly two '/'. Please try again")
                    embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!modify Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                    embedVar.add_field(name="Examples", value="`!modify Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!modify Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                    await message.channel.send(embed=embedVar)
                else:
                    content = content.replace("!modify", "", 1) # Remove "!modify"
                    if (content.split('/')[2][-1] not in ('w', 'd', 'h', 'm')): # The user doesn't select one of the available notify_interval units
                        await message.reply("Error while parsing the notify_interval. Please try again and make sure it is in the correct format.")
                    else:
                        results = await self.parse_registration(content)

                        self.db.edit_user(message.author.id, results["user_jobs_results"], results["user_locations_results"], results["user_notify_interval"])

                        if self.db.check_if_user_exist(message.author.id):
                            # Turn each list into a string and display it to the user
                            user_jobs_string = ", ".join(results["user_jobs_results"])
                            user_locations_string = ", ".join(results["user_locations_results"])

                            embedVar = discord.Embed(title="Registration Successful!", color=0x00ff00)
                            embedVar.add_field(name="Job Keyword(s)", value=user_jobs_string, inline=False)
                            embedVar.add_field(name="Location(s)", value=user_locations_string, inline=False)
                            embedVar.add_field(name="Notify Interval (in minutes)", value=results["user_notify_interval"], inline=False)
                            await message.channel.send(embed=embedVar)
                        else:
                            await message.reply("Registration unsucccessful. Please try again.")
            else:
                await message.reply("You must first register before you can modify your registration")
                embedVar = discord.Embed(title="Jobs Notification registration instructions", description="The format is `!register Job_Keyword(s)/ Location(s)/ Notification_Interval`. In particular, each job/location is separated by a space and if your job/location contains more than one word, it is separated by an underscore.", color=0x00ff00)
                embedVar.add_field(name="Examples", value="`!register Software_Engineer / Edmonton Toronto Los_Angeles/ 1w\n\n!register Software_Developer Data_Engineer/ Edmonton Vancouver Austin/ 3d`", inline=False)
                await message.channel.send(embed=embedVar)

client = GDSCJobClient()
client.run(TOKEN)