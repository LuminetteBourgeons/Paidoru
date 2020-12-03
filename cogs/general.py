import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

with open('cogs/weapons.json') as json_file:
    f_weapons = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:Mod ready")

    def embed_weapon(self, weapon):
        stars = ''
        for i in range(weapon['rarity']):
            stars += '⭐'
        embed = discord.Embed(title=weapon['name'], description=stars,color=0x0197b2)
        embed.set_author(name='Weapon details')
        embed.set_thumbnail(url=weapon['img'])
        embed.add_field(name='Type', value=weapon['type'], inline=True)
        embed.add_field(name='Secondary', value=weapon['secondary'], inline=True)
        embed.add_field(name='Passive', value=weapon['passive'], inline=True)
        embed.add_field(name='Bonus', value=weapon['bonus'], inline=False)
        embed.add_field(name='Location', value=weapon['location'], inline=False)
        return embed

    @commands.command(name='weapon')
    async def cmd_weapon(self,ctx, *keyword):
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
            embed.add_field(name="Syntax : `m. weapon {name}`", value=weapon_list, inline=False)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(General(client))