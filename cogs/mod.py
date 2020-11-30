import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio

from pymongo.collection import Collection

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bot_owner = col_botinfo.find_one()['owner_bot']

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:Mod ready")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        serverinfo = {
            "guild": guild.id,
            "guild_owner": guild.owner.id,
            "greeting":False,
            "greeting_message": "Hai selamat datang di channel ini!",
            "admin": []
        }
        print(serverinfo)
        if col_serverinfo.find_one({'guild': guild.id}) is None:
            col_serverinfo.insert_one(serverinfo)

        user = self.client.get_user(guild.owner.id)
        await user.send('This bot can only be used by server owners, bot owners, and admins')

    @commands.command(name='setup')
    async def cmd_setup(self, ctx):
        if not ctx.guild:
            return
        if ctx.author.id not in [self.bot_owner, ctx.guild.owner.id]:
            return
        serverinfo = {
            "guild": ctx.guild.id,
            "guild_owner": ctx.guild.owner.id,
            "greeting":False,
            "greeting_message":"Hai selamat datang di channel ini!",
            "admin": []
        }
        print(f'{ctx.guild.id}')
        # print(col_serverinfo.find_one({'guild': ctx.guild.id}))
        print(list(col_serverinfo.find()))
        if col_serverinfo.find_one({'guild': ctx.guild.id}) is None:
            col_serverinfo.insert_one(serverinfo)
            await ctx.send(f'{ctx.guild.id}', delete_after=5)
        await ctx.send(f"hi <@{ctx.author.id}>!!!, this server is ready to use mailmod", delete_after=5)


def setup(client):
    client.add_cog(Mod(client))
