from discord.ext import commands
import discord
import pymongo
import json
import asyncio
import os
from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['DISCORD_BOT_TOKEN'], os.environ['MONGO_CLIENT'])



myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])
# myDB = myClient['modmail_gii']
myDB = myClient[os.environ['DB_NAME']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class GreetingMessage(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.emj = [
            '\N{WHITE HEAVY CHECK MARK}',
            '\N{NEGATIVE SQUARED CROSS MARK}'
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        print('cog:greeting ready')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print('new member join')
        if col_serverinfo.find_one()['greeting'] is False:
            return
        # print('new member join 2')
        greet_str = col_serverinfo.find_one({'guild': member.guild.id})['greeting_message']
        srvinf = col_serverinfo.find_one({'guild': member.guild.id})
        channel = self.client.get_channel(srvinf['channel_greeting'])

        msg = greet_str.replace('{user.mention}',member.mention)

        # print(member.guild.id)
        if greet_str is None:
            return
        # await member.send(greet_str)
        await channel.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def run(self, ctx, channel: discord.TextChannel = None):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        if col_serverinfo.find_one({'guild': ctx.guild.id})['greeting'] is True:
            await ctx.send('the command has started', delete_after=3)
            return
        if channel is None:
            return
        confirm_message = await ctx.send('are you sure you want to run the greeting message privately')
        await confirm_message.add_reaction(self.emj[0])
        await confirm_message.add_reaction(self.emj[1])

        def check(reaction, user):
            return str(reaction.emoji) in self.emj and ctx.author == user

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=check)
            # print(str(reaction))
            if str(reaction) == '\N{WHITE HEAVY CHECK MARK}':
                col_serverinfo.update_one({'guild': ctx.guild.id}, {'$set': {'greeting': True, 'channel_greeting': channel.id}})
                await confirm_message.edit(content='the greeting message has started')
            else:
                await confirm_message.edit(content='Canceled')

        except asyncio.TimeoutError:
            await confirm_message.edit(content="You ran out of time!")

    @commands.command(name="stop")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_stop_greeting_message(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        if col_serverinfo.find_one({'guild': ctx.guild.id})['greeting'] is False:
            await ctx.send('the command has stopped', delete_after=5)
            return

        col_serverinfo.update_one({'guild': ctx.guild.id}, {'$set': {'greeting': False}})
        await ctx.send('the greeting message has stopped', delete_after=5)

    @commands.group(name='change')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def group_change(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command passed...')

    @commands.group(name='show')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def group_show(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid git command passed...')

    @group_change.command(name='message')
    async def change_message(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        confirm_message = await ctx.send('are you sure you want to change the greeting message',
                                         delete_after=15)
        await confirm_message.add_reaction(self.emj[0])
        await confirm_message.add_reaction(self.emj[1])
        cmd = 'pai change message '
        users = ctx.author.mention
        col_serverinfo.update_one({'guild': ctx.guild.id},
                                  {'$set': {'greeting_message': ctx.message.content.replace(cmd, '')}})

        def check(reaction, user):
            return str(reaction.emoji) in self.emj and ctx.author == user

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=check)
            # print(str(reaction))
            if str(reaction) == '\N{WHITE HEAVY CHECK MARK}':
                await confirm_message.edit(content='the greeting message has been changed')
            else:
                await confirm_message.edit(content='Canceled')

        except asyncio.TimeoutError:
            await confirm_message.edit(content="You ran out of time!")

    @group_show.command(name='message')
    async def show_message(self, ctx):
        '''
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        if ctx.author == self.client.user:
            return
        users = ctx.author.mention
        message_str = str(col_serverinfo.find_one()['greeting_message'])
        xx = message_str.replace("{user.mention}", users)
        await ctx.send(xx)


def setup(client):
    client.add_cog(GreetingMessage(client))
