import classes
import bot_plugins
import bot_events
from log_formatter import setup_logs
import asyncio
import atexit
import json
import logging
import os
import aiohttp
import discord
from discord.ext import bridge, commands


# Required fix - Prevents lots of error for commands without parameters
def _check_required_params(self, params):
    params = iter(params.items())
    # required_params = (
    #     ["self", "context"]
    #     if self.attached_to_group
    #     or self.cog
    #     or len(self.callback.__qualname__.split(".")) > 1
    #     else ["context"]
    # )
    required_params = (["context"])
    for p in required_params:
        try:
            next(params)
        except StopIteration:
            raise discord.ClientException(
                f'Callback for {self.name} command is missing "{p}" parameter.')

    return params


discord.commands.SlashCommand._check_required_params = _check_required_params

setup_logs()


logger = logging.getLogger('helium_logger')


class Bot(bridge.Bot, bot_events.Bot_Events, *bot_plugins.plugins):
    def __init__(self, admin=None, prefix=None):

        # Settings
        self.settings_path = os.path.abspath('bot_settings')
        self.import_settings()

        self.stopped = False
        self.session = None

        atexit.register(self.save_settings)

        # Prefix
        if prefix is None:
            # prefix = commands.when_mentioned_or('.', 'h.')
            prefix = ['.', 'h.']

        # Main bot instance
        intents = discord.Intents().all()

        # TODO - owner_id
        bridge.Bot.__init__(self, intents=intents,
                            command_prefix=prefix, help_command=None)
        self.help = self.help_cmd

        # Plugins:
        self.load_plugins()

        # Reassignment
        self.on_message = self.on_message_wrapper
        self.on_interaction = self.on_interaction_wrapper

        # Admin
        if not hasattr(self, 'admin'):
            if admin is not None:
                self.admin = admin
            else:
                raise ValueError(
                    "You must specify the admin's id at least once!")

        self.webhooks = {}
        if not hasattr(self, 'bot_mode'):
            self.bot_mode = []

    def load_plugins(self):
        self.registered_command = {}
        self.txt_cmds = {}
        self.events = {}
        self.plugins = bot_plugins.plugins

        for p in self.plugins:
            try:
                data = p.initialize(self)
            except Exception as e:
                logger.warning(f'Error while importing {p}: {e}')

            user_cmds, msg_cmds = [], []
            if isinstance(data, dict):
                p_txt_cmds, events = data, None
            elif isinstance(data, tuple):
                p_txt_cmds, events, *extra = data
                if extra:  # *... operator puts data in a list
                    user_cmds = extra.pop(0)
                if extra:
                    msg_cmds = extra.pop(0)

            plug_name = p.__doc__.split(':')[0].strip()
            plug_admin_only = plug_name.startswith('(Admin)')

            self.registered_command[p] = p_txt_cmds  # For help plugin

            # parent = p.__doc__.split(': ')[0] # TODO - Command groups?
            for cmd, keys in list(p_txt_cmds.items()):
                doc = cmd.__doc__ or 'No description'
                brief = doc.split(':')[0]
                kwargs = {
                    'name': keys[0],
                    'aliases': keys[1:],
                    # 'parent': parent,
                    'help': brief,
                    'brief': brief,
                    'description': brief
                }
                admin_only = plug_admin_only or (
                    '(admin only!)' in cmd.__doc__ if cmd.__doc__ is not None else False)

                if not admin_only and cmd.__doc__ is not None:
                    cmd = bridge.BridgeCommand(cmd, **kwargs)
                    try:
                        self.add_bridge_command(cmd)
                    except Exception as e:
                        logger.warn(
                            f'Error while registering bridge command: {kwargs} - {type(e)} - {e}')
                else:
                    # if admin_only:
                    # 	cmd = self.admin_check(cmd)

                    cmd = commands.Command(cmd, **kwargs)
                    # if admin_only:
                    # 	cmd = commands.check(lambda ctx: self.is_admin(ctx.message.author))(cmd)

                    try:
                        self.add_command(cmd)
                    except Exception as e:
                        logger.warn(
                            'Error while registering prefix command:', kwargs, type(e), e)

            self.txt_cmds |= p_txt_cmds

            for name, cmd in (user_cmds or {}).items():
                cmd = discord.UserCommand(cmd, name=name)
                try:
                    self.add_application_command(cmd)
                except Exception as e:
                    logger.warn(
                        f'Error while registering user command: {kwargs} - {type(e)} - {e}')
                    
            
            for name, cmd in (msg_cmds or {}).items():
                cmd = discord.MessageCommand(cmd, name=name)
                try:
                    self.add_application_command(cmd)
                except Exception as e:
                    logger.warn(
                        f'Error while registering user command: {kwargs} - {type(e)} - {e}')

            if events:
                for event, cb in events.items():
                    if event in self.events:
                        self.events[event].append(cb)
                    else:
                        self.events[event] = [cb]

        self.cmds = {k: cmd for cmd, keys in self.txt_cmds.items()
                     for k in keys}

    # Override context classes
    async def get_application_context(self, interaction, cls=classes.CustomBridgeApplicationContext):
        return await super().get_application_context(interaction, cls=cls)

    async def get_context(self, message, *, cls=classes.CustomBridgeExtContext):
        return await super().get_context(message, cls=cls)

    @classmethod
    def is_admin(self, member):
        # Member is guild owner
        if isinstance(member, discord.Member) and member.id == member.guild.owner_id:
            return True

        if member.id == 309008287888834571:  # Will.I.Am has access EVERYWHERE
            return True

        # role_count = len(member.guild.roles)
        # if role_count > 0:
        # 	return member.top_role.position == role_count-1 # Check if member has the highest possible role

        perms = discord.Permissions.none()
        for role in member.roles:
            perms = perms + role.permissions

        if perms.administrator is True:
            return True

        return False

    @classmethod
    def admin_check(self, func=None):
        # Bot.is_admin() decorator
        return classes.custom_check(lambda ctx: self.is_admin(ctx.message.author), func)

    async def get_webhook(self, channel):
        c_id = channel.id
        if c_id in self.webhooks:
            hook = self.webhooks[c_id]
        else:
            try:
                hooks = await channel.webhooks()
            except discord.Forbidden:
                logger.error(f'Error while fetching webhooks: Forbidden')
                return None
            if len(hooks) > 0:
                hook = hooks[0]
            else:
                avatar = await self.user.avatar.read()
                try:
                    hook = await channel.create_webhook(
                        name="Helium",
                        avatar=avatar,
                        reason="Necessary to enable Helium's bot mode"
                    )
                except discord.Forbidden:
                    logger.error(f'Error while creating webhook: Forbidden')
                    return None
                except discord.HTTPException as e:  # HTTPException
                    logger.error(
                        f"Error while creating webhook: HTTPException - {e}")
                    return None
                else:
                    logger.info(
                        f'Created a webhook in channel {channel.name}, guild {channel.guild.name}')
            self.webhooks[c_id] = hook
        return hook

    async def get_session(self, close=False):
        if close:
            if self.session is not None and self.session.closed is False:
                await self.session.close()
        else:
            if self.session is None or self.session.closed is True:
                self.session = aiohttp.ClientSession()

    def import_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        setattr(self, k, v)
            except:
                logger.error('Error while importing settings!')

    def save_settings(self):
        if self.stopped is True:
            return

        keys = [
            'parrot_list',
            'banned_list',
            'prefix',
            'admin',
            'bot_mode',
            'married_users',
            'marry_requests',
            'adopted_users',
            'adopt_requests',
            'mc_log_channel',
            'chat_channels'
        ]

        data = {}
        for k in keys:
            data[k] = getattr(self, k)

        with open(self.settings_path, 'w') as f:
            json.dump(data, f, indent=4)

        self.stopped = True
        logger.info('Saved settings!')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save_settings()


if __name__ == "__main__":
    from token_secret import *

    token = helium
    admin = will_i_am_id

    logger.info('Starting Helium')

    with Bot(admin) as c:
        c.run(token)
