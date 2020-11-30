import discord
from discord.ext import commands
from datetime import datetime
import pymongo
import json
import asyncio
import math

with open('cogs/dbCred.json') as json_file:
    db_cred = json.load(json_file)

myClient = pymongo.MongoClient(db_cred['client'])
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

        if not message.guild:
            if col_serverinfo.find_one() is None:
                return
            else:
                guild_owner_id = col_serverinfo.find_one()['guild_owner']
                guild_id = col_serverinfo.find_one()['guild']
                print(guild_owner_id)

            if message.author == self.client.user:
                return
            guild_owner = self.client.get_user(guild_owner_id)

            print(f'author : {message.author}')
            print(f'message: {message.content}')

            confirm_emoji = ['\N{WHITE HEAVY CHECK MARK}',
                             '\N{NEGATIVE SQUARED CROSS MARK}',
                             ]
            confirm_message = await message.author.send(content='Is currently contacting the server, please wait')

            embed_confirm = discord.Embed(
                title='Confirmation',
                description=f'You\'re sending this message to {guild_owner.name}?\n'
                            f'React with :white_check_mark: to confirm.\n'
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
                print('check check')
                return str(reaction.emoji) in confirm_emoji and message.author == user

            loop = True

            while loop:
                done, pending = await asyncio.wait([
                    self.client.wait_for('reaction_remove', check=check, timeout=30),
                    self.client.wait_for('reaction_add', check=check, timeout=30)
                ], return_when=asyncio.FIRST_COMPLETED)
                print('check done')
                embed_after_reac = discord.Embed(title='Done')
                try:
                    print('try done')
                    reaction, user = done.pop().result()
                    print('pop done')
                    index = confirm_emoji.index(str(reaction))
                    if index == 0:
                        send_embed = discord.Embed(
                            title='Message Received',
                            description=message.content,
                            colour= discord.Colour.green()
                        )
                        send_embed.set_footer(
                            text=f'{message.author} | m. reply {message.author.id} ',
                            icon_url=message.author.avatar_url
                        )
                        embed_after_reac.title = 'Message Sent'
                        embed_after_reac.description = message.content
                        embed_after_reac.colour = discord.Colour.green()
                        embed_after_reac.set_footer(
                            icon_url=guild_owner.avatar_url,
                            text=f'{guild_owner.name} | {guild_id}'
                        )

                        await guild_owner.send(embed=send_embed)
                    else:
                        embed_after_reac.title = 'Canceled'
                        embed_after_reac.colour = discord.Colour.red()

                    await confirm_message.edit(embed=embed_after_reac)
                    loop = False
                    await confirm_message.remove_reaction(confirm_emoji[0], self.client.user)
                    await confirm_message.remove_reaction(confirm_emoji[1], self.client.user)

                except asyncio.TimeoutError:
                    print('timeout')
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
            return


def setup(client):
    client.add_cog(RedirectMail(client))
