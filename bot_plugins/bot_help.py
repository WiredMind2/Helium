# Discord_bot.py help module

import discord

from discord.ext import bridge, pages
import logging
logger = logging.getLogger('helium_logger')


class Help:
    """Help: test_help"""

    def initialize(self):
        txt_cmds = {
            self.help_cmd: ['help'],
        }

        self.registered_commands = {}

        return txt_cmds

    async def help_cmd(self,
                       ctx,
                       ):
        "Show Helium's help:\n > .help (cat)"

        help_pages = []

        for p in self.plugins:
            try:
                pagegroup = self.get_help_pagegroup(p)
                if pagegroup is not None:
                    help_pages.append(pagegroup)
            except Exception as e:
                logger.warn(f'Error on help, module {p}: {e}')

        if ctx.channel.type in (discord.ChannelType.private, discord.ChannelType.group):
            target_message = 'Here is the bot\'s help!'
        else:
            target_message = "Help page has been sent in your DMs!"

        paginator = pages.Paginator(
            pages=help_pages, show_menu=True, show_disabled=False)

        if isinstance(ctx, bridge.BridgeExtContext):
            await paginator.send(ctx, target=ctx.author, target_message=target_message)
        elif isinstance(ctx, bridge.BridgeApplicationContext):
            await paginator.respond(ctx.interaction, target=ctx.interaction.user, target_message=target_message)

    def get_help_pagegroup(self, p):
        name, arg = p.__doc__.split(':')
        name, arg = name.strip(), arg.strip()
        if name.startswith('(Admin)'):
            return None

        txt_cmds = self.registered_commands[p]
        # txt_cmds = p.initialize(self)
        # if isinstance(txt_cmds, tuple):
        # 	# (txt_cmds, events)
        # 	txt_cmds = txt_cmds[0]

        max_lines = 10
        help_pages = []
        docs = []
        lines = 0
        i = 1
        for f, keys in txt_cmds.items():
            doc = f.__doc__
            if doc is not None and '(admin only!)' not in doc:
                field = {
                    'name': ' | '.join(map(lambda e: '.' + e, keys)),
                    'value': doc
                }
                docs.append(field)
                lines += doc.count('\n') + 1

            if lines >= max_lines:
                emb = {
                    "type": "rich",
                    "title": f"Helium's help - {name}",
                    "description": f"All commands available with Helium's {name} module:",
                    "color": 0x00FFFF,
                    "fields": docs
                }
                emb = discord.Embed.from_dict(emb)
                page = pages.Page(
                    content=f"Helium's help - {name} - page {i + len(help_pages)}",
                    embeds=[emb]
                )
                help_pages.append(page)
                docs = []
                lines = 0

        if len(docs) > 0:
            emb = {
                "type": "rich",
                "title": f"Helium's help - {name}",
                "description": f"All commands available with Helium's {name} module:",
                "color": 0x00FFFF,
                "fields": docs
            }
            emb = discord.Embed.from_dict(emb)
            page = pages.Page(
                content=f"Helium's help - {name} - page {i + len(help_pages)}",
                embeds=[emb]
            )
            help_pages.append(page)

        group = pages.PageGroup(
            pages=help_pages,
            label=f"{name} module",
            description=f"Help for {name} module",
        )

        return group


module_class = Help
