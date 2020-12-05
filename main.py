import discord
from discord.ext import commands, timers, tasks
from discord.ext.commands import CommandNotFound
import asyncio
import json
import pymongo

with open("cred.json") as json_file:
    credentials = json.load(json_file)

PREFIX = credentials['prefix']

intents = discord.Intents.all()
intents.members = True
intents.reactions = True


class mailModGII(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX,
                         intents=intents
                         )
        self.client = commands.Bot

        self.client.remove_command(self, name='help')
        self.token = credentials['token']
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
        game = discord.Game("Chat me")
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
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send(f'channel not found')
        raise error

    def run(self):
        super().run(self.token)


if __name__ == '__main__':
    bot = mailModGII()
    bot.run()
