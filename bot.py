import os

# https://discordpy.readthedocs.io/en/stable/api.html#
import discord

import time
import asyncio
import json
import random
from dotenv import load_dotenv
from Database import Database

# load the envionment variables from .env file
load_dotenv()

TOKEN = os.getenv("API_TOKEN")

interval = int(os.getenv("TIMER_INTERVAL"))

class DemoClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.timer_flag = False
        self.valid_messages = {
            "test": "Welcome to UofA GDSC!",
            "code": "```python\n print('showing how python snippets can be displayed on Discord!')```"
        }
        #use whichever command works with your laptop
        with open('Discord-Bot\greetings.json', 'r') as f:
        #with open('greetings.json', 'r') as f:
            global greetings
            greetings = json.load(f)
        global db
        db = Database()

    async def on_ready(self):
        print(f'{client.user} has connected to Discord!')
    
    async def on_message(self, message):
        # a bot message also count as a message, make sure we don't handle bot's messages
        if message.author == self.user:
            return 

        content = message.content
        if content in self.valid_messages:
            await message.reply(self.valid_messages[content])
    
        if content == "timer":
            if self.timer_flag:
                await message.reply("You can only start one timer at a time!")
            else:
                await message.reply(f"Timer have been started! It will display the current time every {interval} seconds!")
                self.timer_flag = True
                while self.timer_flag:
                    await message.channel.send(f"The current time is: {time.ctime()}")
                    # this await on asyncio.sleep() is very important, try take it out and see what happens...
                    # Note: you will get a RuntimeWarning from asyncio without this await keyword below
                    await asyncio.sleep(interval)
        elif content == "stop":
            if self.timer_flag:
                await message.reply("Timer have been stopped!")
                self.timer_flag = False
            else:
                await message.reply("Timer is not started! Enter \"timer\" to start a timer")
        elif content.lower() == "hello":
            await message.reply(random.choices(greetings['Hello'])[0])
        elif content.lower() == "bye" or content.lower() == "goodbye": 
            await message.reply(random.choices(greetings['Bye'])[0])
        elif content == "db":
            await message.reply(db.check_if_user_exist(message.author.id))
        elif content.lower() == "jobs":
            
            if db.check_if_user_exist(message.author.id):
                keywords_location = db.get_keywords_and_location(message.author.id)
                jobs = db.get_jobs(keywords_location['job_keywords'], keywords_location['location'])

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

client = DemoClient()
client.run(TOKEN)
