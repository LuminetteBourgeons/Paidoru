import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio


with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

with open('cogs/help.json') as json_file:
    f_help = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:Mod ready")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''
        setup server, sama persis kaya fungsi setup
        fungsi cuma berjalan 1x, bila masuk server ke-2 gak berfungsi.
        :param guild:
        :return:
        '''
        serverinfo = {
            "guild": guild.id,
            "guild_owner": guild.owner.id,
            "greeting": False,
            "greeting_message": "Hai selamat datang di channel ini!",
            "reply": {
                "lock": False,
                "target": 0
            }
        }
        print(serverinfo)
        if col_serverinfo.find_one({'guild': guild.id}) is None:
            col_serverinfo.insert_one(serverinfo)

        user = self.client.get_user(guild.owner.id)
        await user.send('This bot can only be used by server owners, bot owners, and admins')

    @commands.command(name='setup')
    @commands.is_owner()
    @commands.guild_only()
    async def cmd_setup(self, ctx):
        '''
        setup cuma pertama kali buat set database,
        bisa sudah di setupm, maka tidak perlu di setup ulang.

        bila ingin setup ulang wajib harus sama developer
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        serverinfo = {
            "guild": ctx.guild.id,
            "guild_owner": ctx.guild.owner.id,
            "greeting": False,
            "greeting_message": "Hai selamat datang di channel ini!",
            "reply": {
                "lock": False,
                "target": 0
            }
        }
        if col_serverinfo.find_one() is None:
            col_serverinfo.insert_one(serverinfo)
            await ctx.send(f"hi <@{ctx.author.id}>!!!, this server is ready to use mailmod", delete_after=5)
        else:
            await ctx.send(f'Server has been setup, contact the bot developer if you want to set it up', delete_after=5)

    def bot_status(self, status):
        '''
        switcher status bot ke objek discord.Status
        :param status: nama status
        :return:
        '''
        switcher = {
            'idle': discord.Status.idle,
            'online': discord.Status.online,
            'offline': discord.Status.offline,
            'dnd': discord.Status.dnd,
            'invisible': discord.Status.invisible
        }
        return switcher.get(status, False)

    @commands.command(name='setbot')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_setbot(self, ctx, status: str):
        '''
        command ganti status bot. dibuat grup biar bisa catch syntax error
        :param ctx:https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param status:
        :return:
        '''
        new_status = self.bot_status(status)

        if new_status is not False:
            await self.client.change_presence(status=new_status)
            await ctx.send(f'Bot status has been changed to `{status}`')
        else:
            await ctx.send('Wrong command lets try `m. setbot <status>` \n'
                           'list of status : `online`, `offline`, `idle`, `dnd`, `invisible`')

    def switch_activity(self, argument):
        '''
        switcher activity str ke objek discord.Activity
        :param argument:
        :return:
        '''
        switcher = {
            'playing': discord.ActivityType.playing,
            'completing': discord.ActivityType.competing,
            'custom': discord.ActivityType.custom,
            'listening': discord.ActivityType.listening,
            'streaming': discord.ActivityType.streaming,
            'unknown': discord.ActivityType.unknown,
            'watching': discord.ActivityType.watching,
        }
        return switcher.get(argument, False)

    @commands.command(name='activity')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_game(self, ctx, activity: str, *name):
        '''
        ganti activity discord
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param activity: str discord activiry
        :param name: nama aktifitas
        :return: none
        '''
        new_activity = self.switch_activity(activity)
        if new_activity is not False:
            if len(name) == 0:
                await ctx.send('<name> cant empty')
                return
            await self.client.change_presence(
                activity=discord.Activity(
                    type=new_activity,
                    name=' '.join(name)
                )
            )
            await ctx.send(f"New Activity {activity} {' '.join(name)}")
        else:
            await ctx.send('Wrong command lets try `m. activity <type> <name>` \n'
                           'list of type : '
                           '`playing`, '
                           '`completing`, '
                           '`custom`, '
                           '`listening`, '
                           '`streaming`, '
                           '`unknown`, '
                           '`watching`')

    @commands.command(name='help')
    async def cmd_help(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        embed = discord.Embed(
            title='list of command',
            description='bot prefix \'m. \'(with <space>)',
            colour=discord.Colour.orange()
        )
        for content in f_help:
            embed.add_field(
                name=content['command'],
                value=content['description'],
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='say')
    @commands.has_permissions(administrator=True)
    async def cmd_say(self, ctx, channel: discord.TextChannel, *msg):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        await channel.send(' '.join(msg))


def setup(client):
    client.add_cog(Mod(client))
