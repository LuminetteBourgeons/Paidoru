import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio
import datetime
import os
with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])
myDB = myClient[db_cred['db_name']]
col_botinfo = myDB['botinfo']
col_serverinfo = myDB['serverinfo']
col_greeting_msg = myDB['greeting_msg']


class RedirectMail(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("cog:RedirectMail ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        fungsi khusus ngecek setiap pesan yang masuk di server
        :param message: https://discordpy.readthedocs.io/en/latest/api.html#message
        :return: none
        '''
        if not message.guild:
            '''
            ngecek DM / bukan
            '''
            if col_serverinfo.find_one() is None:
                return
            else:
                guild_owner_id = col_serverinfo.find_one()['guild_owner']
                guild_id = col_serverinfo.find_one()['guild']
            if message.author == self.client.user:
                return
            guild_owner = self.client.get_user(guild_owner_id)
            if message.author == guild_owner:
                '''
                ngecek guild owner bukan
                '''
                if message.content.startswith('pai'):
                    return
                q = col_serverinfo.find_one({'guild': guild_id})
                if q['reply']['lock']:
                    user = self.client.get_user(q['reply']['target'])
                    embed = discord.Embed(
                        title='Received message',
                        description=message.content,
                        colour=discord.Colour.blue(),
                        timestamp=datetime.datetime.now()
                    )
                    embed.set_footer(
                        text=f'{guild_owner.name}',
                        icon_url=guild_owner.avatar_url
                    )
                    await user.send(embed=embed)

                    embed.title = 'Message Sent'
                    embed.colour = discord.Colour.green()
                    await message.author.send(embed=embed)
                else:
                    await message.author.send('choose user first `pai reply {user id}`')
            else:
                '''
                bila bukan owner, bakal di direct ke owner
                confirm pakai reaction
                
                next buat command buat ngilangin konfirmasi
                pai always confirm
                '''
                confirm_emoji = ['\N{WHITE HEAVY CHECK MARK}',
                                 '\N{NEGATIVE SQUARED CROSS MARK}',
                                 ]
                confirm_message = await message.author.send(content='Is currently contacting the server, please wait')

                embed_confirm = discord.Embed(
                    title='Confirmation',
                    description=f'You\'re sending this message to {guild_owner.name}?\n'
                                f'React with :white_check_mark: to confirpai\n'
                                f'To cancel this request, react with :negative_squared_cross_mark:.',
                    colour=discord.Colour.orange()
                )

                await confirm_message.edit(
                    embed=embed_confirm,
                    content=None
                )
                await confirm_message.add_reaction(confirm_emoji[0])
                await confirm_message.add_reaction(confirm_emoji[1])

                def check(reaction, user):
                    # print('check check')
                    return str(reaction.emoji) in confirm_emoji and message.author == user

                loop = True

                while loop:
                    done, pending = await asyncio.wait([
                        self.client.wait_for('reaction_remove', check=check, timeout=30),
                        self.client.wait_for('reaction_add', check=check, timeout=30)
                    ], return_when=asyncio.FIRST_COMPLETED)
                    # print('check done')
                    embed_after_react = discord.Embed(
                        title='Done',
                        timestamp=datetime.datetime.now())
                    try:
                        # print('try done')
                        reaction, user = done.pop().result()
                        # print('pop done')
                        index = confirm_emoji.index(str(reaction))
                        if index == 0:
                            send_embed = discord.Embed(
                                title='Message Received',
                                description=message.content,
                                colour=discord.Colour.blue(),
                                timestamp=datetime.datetime.now()
                            )
                            send_embed.set_footer(
                                text=f'{message.author} | pai reply {message.author.id} ',
                                icon_url=message.author.avatar_url

                            )
                            embed_after_react.title = 'Message Sent'
                            embed_after_react.description = message.content
                            embed_after_react.colour = discord.Colour.green()
                            embed_after_react.set_footer(
                                icon_url=message.author.avatar_url,
                                text=f'{message.author.name}'
                            )

                            await guild_owner.send(embed=send_embed)
                        else:
                            embed_after_react.title = 'Canceled'
                            embed_after_react.colour = discord.Colour.red()

                        await confirm_message.edit(embed=embed_after_react)
                        loop = False
                        await confirm_message.remove_reaction(confirm_emoji[0], self.client.user)
                        await confirm_message.remove_reaction(confirm_emoji[1], self.client.user)

                    except asyncio.TimeoutError:
                        # print('timeout')
                        await confirm_message.edit(embed=None, content='Time Out')
                        await confirm_message.remove_reaction(confirm_emoji[0], self.client.user)
                        await confirm_message.remove_reaction(confirm_emoji[1], self.client.user)
                        loop = False
                        # If the first finished task died for any reason,
                        # the exception will be replayed here.
                    for future in done:
                        # If any exception happened in any other done tasks
                        # we don't care about the exception, but don't want the noise of
                        # non-retrieved exceptions
                        future.exception()

                    for future in pending:
                        future.cancel()  # we don't need these anymore

    @commands.command(name='reply')
    @commands.is_owner()
    @commands.dm_only()
    async def cmd_lock_DM(self, ctx, user_id: int = None):
        '''
        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :param user_id:
        :return:
        '''
        guild_id = col_serverinfo.find_one()['guild']
        user = self.client.get_user(id=user_id)
        if user is None:
            await ctx.send('wrong id')
        else:
            col_serverinfo.update_one(
                {
                    'guild': guild_id},
                {
                    '$set':
                        {
                            'reply.lock': True,
                            'reply.target': user_id
                        }
                }
            )
            embed = discord.Embed(
                title='-',
                description=f'use `pai exit` to unlock user target',
                timestamp=datetime.datetime.now(),
                color=discord.Colour.orange()
            )
            embed.set_author(
                icon_url=user.avatar_url,
                name=user.name
            )
            embed.set_footer(
                text=f'{user.name} | {user.id}'
            )
            await ctx.send(embed=embed)

    @commands.command(name='exit')
    @commands.is_owner()
    @commands.dm_only()
    async def cmd_unlock_DM(self, ctx):
        '''

        :param ctx: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context
        :return: None
        '''
        guild_id = col_serverinfo.find_one()['guild']
        col_serverinfo.update_one(
            {
                'guild': guild_id},
            {
                '$set':
                    {
                        'reply.lock': False,
                        'reply.target': 0
                    }
            }
        )
        await ctx.send('Exit')


def setup(client):
    client.add_cog(RedirectMail(client))
