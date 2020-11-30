from discord.ext import commands
import discord
import pymongo
import json
import asyncio

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class GreetingMessage(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bot_owner = col_botinfo.find_one()['owner_bot']
        self.emj = [
            '\N{WHITE HEAVY CHECK MARK}',
            '\U0000274e'
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        print('cog:greeting ready')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print('new member join')
        if col_serverinfo.find_one()['greeting'] is False:
            return
        print('new member join 2')
        greet_str = col_serverinfo.find_one({'guild': member.guild.id})['greeting_message']
        print(member.guild.id)
        if greet_str is None:
            return
        await member.send(greet_str)

    @commands.command(name='run')
    async def cmd_start_greeting_message(self, ctx):
        if ctx.author.id not in [self.bot_owner, ctx.guild.owner.id]:
            return
        if col_serverinfo.find_one({'guild': ctx.guild.id})['greeting'] is True:
            await ctx.send('the command has started', delete_after=15)
            return

        approve_message = await ctx.send('are you sure you want to run the greeting message privately',
                                         delete_after=15)
        await approve_message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        await approve_message.add_reaction('\U0000274e')

        def check(reaction, user):
            return str(reaction.emoji) in self.emj and ctx.author == user

        try:
            # Timeout parameter is optional but sometimes can be useful
            reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=check)
            print(str(reaction))
            if str(reaction) == '\N{WHITE HEAVY CHECK MARK}':
                col_serverinfo.update_one({'guild': ctx.guild.id}, {'$set': {'greeting': True}})
                await ctx.send('the greeting message has started', delete_after=5)
                print('approve')

            # await target_user.send(message.content)
        except asyncio.TimeoutError:

            # when wait_for reaches specified timeout duration (in this example it is 30 seconds)
            await ctx.send("You ran out of time!")

    @commands.command(name="stop")
    async def cmd_stop_greeting_message(self, ctx):
        if ctx.author.id not in [self.bot_owner, ctx.guild.owner.id]:
            return
        if col_serverinfo.find_one({'guild': ctx.guild.id})['greeting'] is False:
            await ctx.send('the command has stopped', delete_after=5)
            return

        approve_message = await ctx.send('are you sure you want to stop the greeting message privately',
                                         delete_after=15)
        await approve_message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        await approve_message.add_reaction('\U0000274e')

        def check(reaction, user):
            return str(reaction.emoji) in self.emj and ctx.author == user

        try:
            # Timeout parameter is optional but sometimes can be useful
            reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=check)
            print(str(reaction))
            if str(reaction) == '\N{WHITE HEAVY CHECK MARK}':
                col_serverinfo.update_one({'guild': ctx.guild.id}, {'$set': {'greeting': False}})
                await ctx.send('the greeting message has started', delete_after=5)
                print('approve')

            # await target_user.send(message.content)
        except asyncio.TimeoutError:

            # when wait_for reaches specified timeout duration (in this example it is 30 seconds)
            await ctx.send("You ran out of time!")

    @commands.command(name='message')
    async def cmd_change_greeting_message(self, ctx):
        print(ctx.message.content)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return


def setup(client):
    client.add_cog(GreetingMessage(client))
