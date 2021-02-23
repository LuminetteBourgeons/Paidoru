import discord
from discord.ext import commands, timers, tasks
from discord.ext.commands import CommandNotFound
from datetime import datetime
import asyncio
import json
import pymongo
import os


# DB_NAME
PREFIX = ['pai ', 'Pai ', ';', '; ']

intents = discord.Intents.all()
intents.members = True
intents.reactions = True


myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])
# myDB = myClient['modmail_gii']
myDB = myClient[os.environ['DB_NAME']]
col_bot_log = myDB['bot_log']


class mailModGII(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX,
                         intents=intents
                         )
        self.client = commands.Bot

        self.client.remove_command(self, name='help')
        self.client.remove_command(self, name='stop')
        self.load_extension('cogs.redirectmail')
        self.load_extension('cogs.greeting')
        self.load_extension('cogs.mod')
        self.load_extension('cogs.general')

    async def on_ready(self):

        print('Logged on as', self.user)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        game = discord.Game("Hi Sayang")
        col_bot_log.insert_one(
            {
                "name": "start up",
                "timestamp": datetime.now()
            }
        )
        await self.client.change_presence(self, status=discord.Status.online, activity=game)

    async def on_command_error(self, ctx, error):
        '''
        semua error di handling di sini
        :param ctx:
        :param error:
        :return:
        '''
        if isinstance(error, CommandNotFound):
            return

        if isinstance(error, commands.CheckFailure):
            return

        if isinstance(error, commands.ChannelNotFound):
            await ctx.send(f'channel not found')
            return
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f'error')
            return
        raise error

    def run(self):
        super().run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    bot = mailModGII()
    bot.run()
