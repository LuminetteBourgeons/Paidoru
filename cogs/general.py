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


with open('cogs/weapons.json') as json_file:
    f_weapons = json.load(json_file)

with open('cogs/artifacts.json') as json_file:
    f_artifacts = json.load(json_file)

with open('cogs/help.json') as json_file:
    f_help = json.load(json_file)

myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])
# myDB = myClient['modmail_gii']
myDB = myClient[os.environ['DB_NAME']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']
col_disable = myDB['disable']
col_command_log = myDB['command_log']
col_tags = myDB['tags']
col_fun = myDB['fun']


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:Mod ready")

    def checker(self, command):
        async def predicate(ctx):
            print(ctx.channel.id)
            print(command)
            is_disabled = col_disable.find_one(
                {
                    "command": command,
                    "channel": ctx.channel.id
                }
            )
            print(is_disabled is None)
            return is_disabled is None

        return commands.check(predicate)

    def command_log(self, user, command, level, content):
        col_command_log.insert_one(
            {
                "user": user,
                "command": command,
                "content": content,
                "level": level,
                "timestamp": datetime.now()
            }
        )

    def embed_weapon(self, weapon):
        '''
        Fungsi cuma buat konversi json weapon jadi embed
        :param weapon:
        :return:
        '''
        stars = ''
        for i in range(weapon['rarity']):
            stars += ' ⭐'
        embed = discord.Embed(title=weapon['name'], description=stars, color=0x0197b2)
        embed.set_author(name='Weapon details')
        embed.set_thumbnail(url=weapon['img'])
        embed.add_field(name='Type', value=weapon['type'], inline=True)
        embed.add_field(name='Rarity', value=weapon['rarity'], inline=True)
        embed.add_field(name='Secondary', value=weapon['secondary'], inline=True)
        embed.add_field(name='Passive', value=weapon['passive'], inline=True)
        embed.add_field(name='Base ATK', value=weapon['atk'], inline=True)
        embed.add_field(name='Location', value=weapon['location'], inline=True)
        embed.add_field(name='Bonus', value=weapon['bonus'], inline=False)

        return embed

    @commands.command(name='w')
    @checker(None, "weapon")
    async def cmd_weapon(self, ctx, *keyword):
        '''

        :param ctx:https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param keyword: nama senjata
        :return:
        '''
        keyword = ' '.join(keyword).lower()
        count = 0
        find_list = []
        find_one = None
        for weapon in f_weapons:
            name = weapon['name'].lower()
            if keyword.lower() == weapon['name'].lower():
                embed = self.embed_weapon(weapon)
                await ctx.send(embed=embed)
                self.command_log(ctx.author.id, 'weapon', 'general', weapon['name'])
                return
            elif len(keyword) >= 4:
                if name.find(keyword) >= 0:
                    find_one = weapon
                    find_list.append(weapon)
                    count += 1
        if count == 0:
            embed = discord.Embed(
                description="Weapon not found",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        elif count == 1:
            embed = self.embed_weapon(find_one)
            await ctx.send(embed=embed)
        else:
            weapon_list = ''
            for weapon in find_list:
                weapon_list += f"{weapon['name']}\n"
            embed = discord.Embed(color=0xecf005)
            embed.set_author(name=f"{count} weapons found\n"
                                  f"Please choose one")
            embed.add_field(name="Syntax : `pai weapon {name}`", value=weapon_list, inline=False)
            await ctx.send(embed=embed)
        if count != 0:
            self.command_log(ctx.author.id, 'weapon', 'general', find_one['name'])
        print('save db')

    def embed_artifact(self, artifact):
        '''
        Fungsi cuma buat konversi json artifact jadi embed
        :param artifact:
        :return:
        '''
        stars = ''
        embed = discord.Embed(title=artifact['set'], description=stars, color=0x0197b2)
        embed.set_author(name='Artifact details')
        embed.set_thumbnail(url=artifact['img'])
        embed.add_field(name='Max Rarity', value=artifact['max-rarity'], inline=False)
        embed.add_field(name='2-Piece Bonus', value=artifact['2-set bonus'], inline=False)
        embed.add_field(name='4-Piece Bonus', value=artifact['4-set bonus'], inline=False)
        return embed

    @commands.command(name='a')
    @checker(None, "artifact")
    async def cmd_artifact(self, ctx, *keyword):
        '''

        :param ctx:https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param keyword: nama senjata
        :return:
        '''
        keyword = ' '.join(keyword).lower()
        count = 0
        find_list = []
        find_one = None
        for artifact in f_artifacts:
            name = artifact['set'].lower()
            if keyword.lower() == artifact['set'].lower():
                embed = self.embed_artifact(artifact)
                await ctx.send(embed=embed)
                self.command_log(ctx.author.id, 'artifact', 'general', artifact['set'])
                return
            elif len(keyword) >= 4:
                if name.find(keyword) >= 0:
                    find_one = artifact
                    find_list.append(artifact)
                    count += 1
        if count == 0:
            embed = discord.Embed(
                description="Artifact not found",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        elif count == 1:
            embed = self.embed_artifact(find_one)
            await ctx.send(embed=embed)
        else:
            artifact_list = ''
            for artifact in find_list:
                artifact_list += f"{artifact['set']}\n"
            embed = discord.Embed(color=0xecf005)
            embed.set_author(name=f"{count} artifact found\n"
                                  f"Please choose one")
            embed.add_field(name="Syntax : `pai artifact {name}`", value=artifact_list, inline=False)
            await ctx.send(embed=embed)
        if count != 0:
            self.command_log(ctx.author.id, 'artifact', 'general', find_one['set'])

    @commands.command(name='calc')
    @checker(None, "calc")
    async def cmd_calc(self, ctx, *, q):
        await ctx.send("{:,}".format(eval(q)))

    @commands.command(name='help')
    @checker(None, "help")
    async def cmd_help(self, ctx, command=None):
        """

        :param command:
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        """

        general_list = ''
        for helping in f_help:
            if helping['type'] == 'General':
                general_list += f" {helping['name']}\n"
        if command is None:
            embed = discord.Embed(
                title='list of command',
                description='bot prefix `pai `'
                            '\nType `pai help {command}`',
                colour=discord.Colour.orange()
            )
            embed.add_field(
                name='General',
                value=general_list,
                inline=True
            )
            await ctx.send(embed=embed)
        else:
            for helping in f_help:
                if helping['name'] == command and helping['type'] == 'General':
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

    @commands.command(name='avatar')
    @checker(None, "avatar")
    async def cmd_avatar(self, ctx, user: discord.User = None):
        """

        :param user: https://discordpy.readthedocs.io/en/latest/api.html#user
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return:
        """
        pass
        if user is None:
            user = ctx.author
        embed = discord.Embed(
            title=f'Direct link.',
            url=f"{user.avatar_url}",
            colour=discord.Colour.green()
        )

        embed.set_image(
            url=user.avatar_url
        )
        embed.set_author(
            icon_url=user.avatar_url,
            name=f'{user.name}\'s profile picture.'
        )

        await ctx.send(embed=embed)
        self.command_log(ctx.author.id, 'avatar', 'general', f'{user}')

    @commands.command(name='tag')
    @checker(None, "tag")
    async def cmd_tag(self, ctx, *, tag):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param tag: tag
        :return:
        '''
        find_tag = col_tags.find_one(
            {
                'tag': tag
            }
        )
        if find_tag is not None:
            if find_tag['type'].lower() == 'embed'.lower():
                embed = discord.Embed(
                    description=find_tag['description'],
                    color=discord.Colour.orange()
                )
                await ctx.send(embed=embed)
            elif find_tag['type'].lower() == 'json'.lower():
                f = json.loads(str(find_tag['description']))
                test_embed = discord.Embed.from_dict(f)
                await ctx.send(embed=test_embed)
            else:
                await ctx.send(find_tag['description'])

    @commands.command(name='taglist')
    @checker(None, "taglist")
    async def cmd_taglist(self, ctx):
        find_tag = list(col_tags.find({'tag': {'$exists': True}}))
        tags_string = ''
        for tag in find_tag:
            tags_string += f" `{tag['tag']}`,"
        tags_string = tags_string[0:len(tags_string) - 1]
        await ctx.send(tags_string)

    @commands.command(name='hug')
    @checker(None, "hug")
    async def cmd_hug(self, ctx, user: discord.User = None):
        if user is None:
            return
        if user == ctx.author:
            message = await ctx.send("Can't hug yourself")
            await message.add_reaction('\U0001f1eb')
            return
        img_url = list(col_fun.find({'hug': {'$exists': True}}))[0]['hug']
        img = random.choice(img_url)
        embed = discord.Embed(
            color=discord.Colour.blue(),
            title=f"{ctx.author.name} hugs {user.name}"
        )
        embed.set_image(
            url=img
        )
        await ctx.send(embed=embed)

    @commands.command(name='kiss')
    @checker(None, "kiss")
    async def cmd_kiss(self, ctx, user: discord.User = None):
        if user is None:
            return
        if user == ctx.author:
            message = await ctx.send("Can't kiss yourself")
            await message.add_reaction('\U0001f1eb')
            return
        img_url = list(col_fun.find({'kiss': {'$exists': True}}))[0]['kiss']
        img = random.choice(img_url)
        embed = discord.Embed(
            color=discord.Colour.blue(),
            title=f"{ctx.author.name} kiss {user.name}"
        )
        embed.set_image(
            url=img
        )
        await ctx.send(embed=embed)

    @commands.command(name='pat')
    @checker(None, "pat")
    async def cmd_pats(self, ctx, user: discord.User = None):
        if user is None:
            return
        if user == ctx.author:
            message = await ctx.send("Can't pat yourself")
            await message.add_reaction('\U0001f1eb')
            return
        img_url = list(col_fun.find({'pat': {'$exists': True}}))[0]['pat']
        img = random.choice(img_url)
        embed = discord.Embed(
            color=discord.Colour.blue(),
            title=f"{ctx.author.name} pats {user.name}"
        )
        embed.set_image(
            url=img
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        pass


def setup(client):
    client.add_cog(General(client))
