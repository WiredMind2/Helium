# Discord_bot.py admin module

import asyncio
import discord

from discord.ext import bridge, pages
import logging
logger = logging.getLogger('helium_logger')


class Admin:
    """(Admin) Admin stuff: admin"""

    def initialize(self):
        txt_cmds = {
            self.list_servers: ['list_servers'],
            self.server_info: ['server_info']
        }

        self.registered_commands = {}

        return txt_cmds

    async def list_servers(self, ctx):
        "List all servers that Helium joined (Admin only!)"

        if not self.is_admin(ctx.author):
            ctx.respond(f'Only the bot\'s admin can use this command!')
            return

        coros = []
        c = ctx.respond(f'Helium joined {len(self.guilds)} guilds:')
        coros.append(c)
        for guild in self.guilds:
            text = f'{guild.name} ({guild.id}) - {guild.owner}'
            c = ctx.send(text)
            coros.append(c)
        await asyncio.gather(*coros)

    @discord.option(
        'id',
        description="The guild id"
    )
    async def server_info(self,
                          ctx,
                          id: int
                          ):
        "Get infos on a specific guild (admin only!)"

        if not self.is_admin(ctx.author):
            await ctx.respond(f'Only admins can use this command!')
            return

        guild = self.get_guild(id)
        if guild is None:
            try:
                guild = await self.fetch_guild(id, with_counts=True)
            except discord.Forbidden:
                pass

        if guild is None:
            await ctx.respond(f'Guild with id {id} was not found!')

        try:
            invites = list(map(lambda i: i.code, await guild.invites()))
        except discord.Forbidden:
            invites = ['Unknown']

        data = {
            'id': guild.id,
            'name': guild.name,
            'description': guild.description,
            'owner': f'{guild.owner.name}#{guild.owner.discriminator}',
            'members': len(guild.members) if guild.members is not None else guild.approximate_member_count,
            # 'members': guild.member_count
            'channels': len(guild.channels) if guild.channels is not None else 'Unknown',
            'roles': len(guild.roles),
            'invites': str(invites),
            'icon': guild.icon.url
        }

        await ctx.respond('\n'.join(map(lambda e: f'{e[0]}: {e[1]}', data.items())))


module_class = Admin
