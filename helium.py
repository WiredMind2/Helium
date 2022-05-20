import atexit
import json
import logging
# import logging.handlers
import os

import discord
from discord.ext import bridge, commands

import bot_events
# import user_api
import bot_plugins
import classes
from log_formatter import setup_logs

setup_logs()

logger = logging.getLogger('helium_logger')

class Bot(bridge.Bot, bot_events.Bot_Events, *bot_plugins.plugins):
	def __init__(self, admin=None, prefix=None):

		# Settings
		self.settings_path = os.path.abspath('bot_settings')
		self.import_settings()

		atexit.register(self.save_settings)

		# Prefix
		if prefix is None:
			prefix = commands.when_mentioned_or('.', 'h.')

		# Main bot instance
		intents = discord.Intents().all()
		# TODO - owner_id
		bridge.Bot.__init__(self, intents=intents, command_prefix=prefix)

		# Plugins:
		self.load_plugins()

		# Reassignment
		self.on_message = self.on_message_wrapper

		# Admin
		if not hasattr(self, 'admin'):
			if admin is not None:
				self.admin = admin
			else:
				raise ValueError("You must specify the admin's id at least once!")

		self.webhooks = {}
		if not hasattr(self, 'bot_mode'):
			self.bot_mode = []

	def load_plugins(self):
		self.txt_cmds = {}
		self.events = {}
		self.plugins = bot_plugins.plugins

		for p in self.plugins:
			try:
				data = p.initialize(self)
			except Exception as e:
				logger.warn(f'Error while importing {p}: {e}')

			if isinstance(data, dict):
				p_txt_cmds, events = data, None
			elif isinstance(data, tuple):
				p_txt_cmds, events = data

			# TODO - Help command
			plug_name = p.__doc__.split(':')[0].strip()
			if not plug_name.startswith('(Admin)'):
				# parent = p.__doc__.split(': ')[0] # TODO - Command groups?
				for cmd, keys in list(p_txt_cmds.items()):
					if cmd.__doc__ is not None and '(admin only!)' not in cmd.__doc__:
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
						cmd = bridge.BridgeCommand(cmd, **kwargs)
						try:
							self.add_bridge_command(cmd)
						except Exception as e:
							print(kwargs, type(e), e)

				self.txt_cmds |= p_txt_cmds

			if events:
				for event, cb in events.items():
					if event in self.events:
						self.events[event].append(cb)
					else:
						self.events[event] = [cb]
		
		self.cmds = {k:cmd for cmd, keys in self.txt_cmds.items() for k in keys}

	# Override context classes
	async def get_application_context(self, interaction, cls=classes.CustomBridgeApplicationContext):
		return await super().get_application_context(interaction, cls=cls)
		
	async def get_context(self, message, *, cls=classes.CustomBridgeExtContext):
		return await super().get_context(message, cls=cls)

	def is_admin(self, member):
		if member.id == member.guild.owner_id: # Member is guild owner
			return True

		role_count = len(member.guild.roles)
		if role_count > 0:
			return member.top_role.position == role_count-1 # Check if member has the highest possible role

		return False

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
				except discord.HTTPException as e: # HTTPException
					logger.error(f"Error while creating webhook: HTTPException - {e}")
					return None
				else:
					logger.info(f'Created a webhook in channel {channel.name}, guild {channel.guild.name}')
			self.webhooks[c_id] = hook
		return hook

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
			'mc_log_channel'
		]

		data = {}
		for k in keys:
			data[k] = getattr(self, k)

		with open(self.settings_path, 'w') as f:
			json.dump(data, f, indent=4)

		logger.info('Saved settings!')

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.save_settings()


if __name__ == "__main__":
	from token_secret import *

	token = helium
	admin = will_i_am_id

	with Bot(admin) as c:
		c.run(token)
