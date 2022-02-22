import os

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
        # a bot message also count as a message, make sure we don't handle bot's messages
        if message.author == self.user:
            return 

        content = message.content
        if content in self.valid_messages:
            await message.reply(self.valid_messages[content])
        elif content.lower() == "notify":
            await self.manage_notification(message)
        elif content.lower() == "hello":
            await message.reply(random.choices(greetings['Hello'])[0])
        elif content.lower() == "bye" or content.lower() == "goodbye": 
            await message.reply(random.choices(greetings['Bye'])[0])
        elif content == "db":
            await message.reply(self.db.check_if_user_exist(message.author.id))
        elif content.lower() == "jobs":
            if self.db.check_if_user_exist(message.author.id):
                keywords_location = self.db.get_keywords_and_location(message.author.id)
                jobs = self.db.get_jobs(keywords_location['job_keywords'], keywords_location['location'])

                #Right now there is a 4000 message limit
                '''
                job_display = ""
                for job in jobs:
                    job_line = f"Title: {job[0]}, Company: {job[1]}, Location: {job[2]}, URL: {job[3]}\n\n"
                    job_display+=job_line
                print(f"KEYWORDS LOCATION IS {keywords_location}")
                print(f"JOBS IS {jobs}")
                print(db.get_jobs(["software"], ["Edmonton"])) 
                print(f"JOB DISPLAY {job_display}")
                '''

                job = jobs[0]
                await message.reply(f"Title: {job[0]}, Company: {job[1]}, Location: {job[2]}, URL: {job[3]}\n")
                #await message.reply(job_display)
                #await message.reply(db.get_keywords_and_location(message.author.id))
            else:
                await message.reply(f"You haven't registered your job keywords and location yet, your id is {message.author.id}")

client = GDSCJobClient()
client.run(TOKEN)
