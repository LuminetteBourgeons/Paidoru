import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio
import os
import random
from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['DISCORD_BOT_TOKEN'], os.environ['MONGO_CLIENT'])


with open('cogs/help.json') as json_file:
    f_help = json.load(json_file)

myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])
myDB = myClient['modmail_gii']
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']
col_disable = myDB['disable']
col_tags = myDB['tags']
col_member = myDB['members']
col_fun = myDB['fun']


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
            await ctx.send('Wrong command lets try `pai setbot <status>` \n'
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
            await ctx.send('Wrong command lets try `pai activity <type> <name>` \n'
                           'list of type : '
                           '`playing`, '
                           '`completing`, '
                           '`custom`, '
                           '`listening`, '
                           '`streaming`, '
                           '`unknown`, '
                           '`watching`')

    @commands.command(name='playing')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_playing(self, ctx, *, name):
        if len(name) == 0:
            await ctx.send('<name> cant empty')
            return
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=name
            )
        )
        await ctx.send(f"New activity playing {name}")

    @commands.command(name='listening')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_listening(self, ctx, *, name):
        if len(name) == 0:
            await ctx.send('<name> cant empty')
            return
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=name
            )
        )
        await ctx.send(f"New activity listening {name}")

    @commands.command(name='watching')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_watching(self, ctx, *, name):
        if len(name) == 0:
            await ctx.send('<name> cant empty')
            return
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=name
            )
        )
        await ctx.send(f"New activity watching {name}")

    @commands.command(name='modhelp')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_modhelp(self, ctx, command=None):
        """

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        """
        owner_list = ''
        admin_list = ''
        general_list = ''
        for helping in f_help:
            if helping['type'] == 'Guild Owner':
                owner_list += f" {helping['name']}\n"
            elif helping['type'] == 'Administrator':
                admin_list += f" {helping['name']}\n"
            elif helping['type'] == 'General':
                general_list += f" {helping['name']}\n"
        if command is None:
            embed = discord.Embed(
                title='list of command',
                description='bot prefix `pai `'
                            '\nType `pai modhelp {command}`',
                colour=discord.Colour.orange()
            )
            embed.add_field(
                name='Owner',
                value=owner_list,
                inline=True
            )
            embed.add_field(
                name='Administrator',
                value=admin_list,
                inline=True
            )
            embed.add_field(
                name='General',
                value=general_list,
                inline=True
            )
            embed.set_footer(
                text='Owner can use all commands\n'
                     'Administrators cannot use owner commands\n'
                     'General cannot use the admin and owner commands'
            )
            await ctx.send(embed=embed)
        else:
            for helping in f_help:
                if helping['name'] == command:
                    embed = discord.Embed(
                        title=f"Detail of `{helping['name']}` command",
                        colour=discord.Colour.orange()
                    )
                    embed.add_field(
                        name=f"Syntax",
                        value=helping['syntax'],
                        inline=False
                    )
                    embed.add_field(
                        name=f"Description",
                        value=helping['description'],
                        inline=False
                    )
                    await ctx.send(embed=embed)
                    return
            await ctx.send('command not found')

    @commands.command(name='say')
    async def cmd_say(self, ctx, channel: discord.TextChannel, *msg):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        '''
        await channel.send(' '.join(msg))

    @commands.command(name='disable')
    @commands.has_permissions(administrator=True)
    async def cmd_disable(self, ctx, command):
        msg = ctx.message
        found = False
        for helping in f_help:
            if helping['name'] == command and helping['type'] == 'General':
                found = True

        if found:
            check_command = col_disable.find_one(
                {
                    "command": command
                }
            )

            if check_command is None:
                col_disable.insert_one(
                    {
                        "command": command,
                        "channel": [ctx.channel.id]
                    }
                )
            is_disabled = col_disable.find_one(
                {
                    "command": command,
                    "channel": ctx.channel.id
                }
            )
            print(is_disabled)
            if is_disabled is None:
                col_disable.update(
                    {
                        "command": command
                    },
                    {
                        "$push": {
                            "channel": ctx.channel.id
                        }
                    }
                )
                await ctx.send("Done !", delete_after=5)
            else:
                await ctx.send("This command already", delete_after=5)
        else:
            await ctx.send("command not found", delete_after=5)
        await msg.delete()

    @commands.command(name='enable')
    @commands.has_permissions(administrator=True)
    async def cmd_enable(self, ctx, command):
        msg = ctx.message
        found = False

        for helping in f_help:
            if helping['name'] == command and helping['type'] == 'General':
                found = True

        if found:
            check_command = col_disable.find_one(
                {
                    "command": command
                }
            )

            if check_command is None:
                return
            is_disabled = col_disable.find_one(
                {
                    "command": command,
                    "channel": ctx.channel.id
                }
            )
            print(f'exec enable {is_disabled is not None}')
            if is_disabled is not None:
                col_disable.update(
                    {
                        "command": command
                    },
                    {
                        "$pull": {
                            "channel": ctx.channel.id
                        }
                    }
                )
                await ctx.send("This command has enable on this channel", delete_after=5)

        else:
            await ctx.send("command not found", delete_after=5)
        await msg.delete()

    @commands.command(name='tagadd')
    @commands.has_permissions(administrator=True)
    async def cmd_tagadd(self, ctx, isembed: str = 'nonEmbed'):
        if isembed.lower() not in ['nonembed', 'embed']:
            return
        await ctx.send('type a tag (15s timeout), type `cancel` for abort')
        print(ctx.message.channel)

        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.author

        tag = ''
        description = ''
        try:
            message = await self.client.wait_for('message', timeout=15, check=check)
            if message.content.lower() == 'cancel':
                await ctx.send('aborted')
                return
            tag = message.content
            print(message.content)
        except asyncio.TimeoutError:
            await ctx.send('timeout')
            return

        find_tag = col_tags.find_one({"tag": tag})
        print(find_tag)
        if find_tag is not None:
            await ctx.send('the tag is already')
            return
        await ctx.send('type a tag\'s description (60s timeout), type `cancel` for abort')
        try:
            message = await self.client.wait_for('message', timeout=60, check=check)
            if message.content.lower() == 'cancel':
                await ctx.send('aborted')
                return
            description = message.content
            print(message.content)
        except asyncio.TimeoutError:
            await ctx.send('timeout')
            return

        await ctx.send(f'the tag `{tag}` has been added\n'
                       f'the description is:\n'
                       f'--\n'
                       )
        if isembed.lower() == 'embed':
            embed = discord.Embed(
                description=description,
                color=discord.Colour.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(description)

        col_tags.insert_one(
            {
                "creator": ctx.author.id,
                "type": isembed,
                "tag": tag,
                "description": description
            }
        )

    @commands.command(name='tagremove')
    @commands.has_permissions(administrator=True)
    async def cmd_tagremove(self, ctx, *, tag):
        find_tag = col_tags.find_one(
            {
                'tag': tag
            }
        )
        if find_tag is not None:
            col_tags.delete_one(
                {
                    "tag": tag
                }
            )
            await ctx.send(f'tag {tag} has been removed!')

    @commands.command(name='emjinfo')
    @commands.has_permissions(administrator=True)
    async def cmd_emoji_info(self, ctx, emoji: discord.Emoji = None):
        name = emoji.name
        emoji_id = emoji.id

        await ctx.send(f'`<:{name}:{emoji_id}>`')

    @commands.command(name='scanchannel')
    @commands.has_permissions(administrator=True)
    async def cmd_scanchannel(self, ctx):
        print(ctx.message.channel.id)
        print(ctx.guild.id)
        check1 = col_serverinfo.find_one(
            {
                "guild": ctx.guild.id,
                "grab_data": ctx.message.channel.id
            }
        )
        await ctx.message.delete();
        if check1 is not None:
            await ctx.send("This channel already scanned", delete_after=5)
            return
        col_serverinfo.update(
            {
                "guild": ctx.guild.id
            },
            {
                "$push": {
                    "grab_data": ctx.channel.id
                }
            }
        )

    @commands.command(name='stopscan')
    @commands.has_permissions(administrator=True)
    async def cmd_stopscan(self, ctx):
        check1 = col_serverinfo.find_one(
            {
                "guild": ctx.guild.id,
                "grab_data": ctx.message.channel.id
            }
        )
        if check1 is None:
            return
        else:
            pass
            col_serverinfo.update(
                {
                    "guild": ctx.guild.id
                },
                {
                    "$pull": {
                        "grab_data": ctx.channel.id
                    }
                }
            )
            await ctx.send('done!', delete_after=5)

    @commands.command(name='grabimage')
    @commands.has_permissions(administrator=True)
    async def cmd_grabimage(self, ctx,limit: int = 10, user: discord.User = None):
        await ctx.message.delete()

        messages = await ctx.channel.history(limit=limit).flatten()
        for each in messages:
            attachments = each.attachments
            if user is not None:
                if len(attachments) == 0 or each.author != user:
                    continue
            elif len(attachments) == 0:
                continue

            for attachment in attachments:
                # print(attachment.url[len(attachment.url)-1])
                # print(type(attachment.url))
                format2 = attachment.url.split('.')
                format2 = format2[len(format2)-1]
                await ctx.author.send(f"<{attachment.url}> {each.author.name.replace(' ','_')}_{attachment.id}.{format2}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        # print(message.type.name)
        if message.type.name == 'premium_guild_subscription':
        # if message.type.name == 'default':
            embed = discord.Embed(
                timestamp=datetime.today(),
                colour=discord.Colour.green(),
                description=f"**{message.author.name}**, Terimakasih telah mengsupport server kami."
            )
            img_url = list(col_fun.find({'thanks': {'$exists': True}}))[0]['thanks']
            img = random.choice(img_url)
            embed.set_image(url=img)
            channel = message.channel

            await channel.send(embed=embed)
        check1 = col_serverinfo.find_one(
            {
                "guild": message.guild.id,
                "grab_data": message.channel.id
            }
        )
        if check1 is not None:

            # if 'stopscan' in message.content:
            #     return
            if message.channel.id in check1['grab_data']:
                channel = self.client.get_channel(message.channel.id)

                raw = message.content.split('\n')
                nick = ''
                uid = ''
                server = ''
                for data in raw:
                    data = data.split(':')
                    if (data[0]).lower() == 'nick':
                        nick = data[1]
                    elif (data[0]).lower() == 'uid':
                        uid = data[1]
                    elif (data[0]).lower() == 'server':
                        server = data[1]

                if nick == '' or uid == '' or server == '':
                    await message.add_reaction('\U0000274c')
                    temp = await channel.send(f"<@{message.author.id}>, masukan data sesuai format")
                    await asyncio.sleep(5)
                    await message.delete()
                    await temp.delete()
                else:
                    find_members = col_member.find_one(
                        {
                            "user": message.author.id,
                            "uid": uid
                        }
                    )
                    if find_members is None:
                        col_member.insert_one(
                            {
                                "user": message.author.id,
                                "uid": uid,
                                "nick": nick,
                                "server": server
                            }
                        )
                        await message.add_reaction('\U00002705')
                        await channel.send(f"Terimakasih <@{message.author.id}>, sudah mengisi sesuai format", delete_after=5)
                    else:
                        await message.add_reaction('\U0000274c')
                        temp = await channel.send(f"<@{message.author.id}>,"
                                                  f" Anda sudah memasukan data ini, terimakasih :D")
                        await asyncio.sleep(10)
                        await message.delete()
                        await temp.delete()


    @commands.command(name='autoscan')
    @commands.has_permissions(administrator=True)
    async def cmd_autoscan(self, ctx, limit: int = 100):
        messages = await ctx.channel.history(limit=limit).flatten()
        for message in messages:
            # print(f'{message}\n')
            raw = message.content.split('\n')
            nick = ''
            uid = ''
            server = ''
            for data in raw:
                data = data.split(':')
                print(data)
                if (data[0]).lower().strip() in ['ign','nick']:
                    nick = data[1]
                elif (data[0]).lower().strip() == 'uid':
                    uid = data[1]
                elif (data[0]).lower().strip() == 'server':
                    server = data[1]

            if nick == '' or uid == '' or server == '':
                pass
                # await message.add_reaction('\U0000274c')
            else:
                find_member = col_member.find_one(
                    {
                        "user": message.author.id,
                        "uid": uid
                    }
                )
                print(find_member)
                if find_member is None:
                    col_member.insert_one(
                        {
                            "user": message.author.id,
                            "uid": uid,
                            "nick": nick,
                            "server": server
                        }
                    )
                    await message.add_reaction('\U00002705')
                else:
                    pass
                    # await message.add_reaction('\U0000274c')

    @commands.command(name='eval')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_eval(self, ctx, *, content):
        print(content)
        await ctx.send(eval(content))

    @commands.command(name='connect')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_connect(self, ctx, timeout=60):
        channel = ctx.author.voice.channel
        print(type(channel))
        await channel.connect(timeout=timeout)
        await ctx.message.delete()

    @commands.command(name='disconnect')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cmd_disconnect(self, ctx):
        # channel = ctx.member.voice
        await ctx.voice_client.disconnect()
        await ctx.message.delete()

def setup(client):
    client.add_cog(Mod(client))
