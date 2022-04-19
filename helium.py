import discord

from discord.ext import commands
from discord import ApplicationContext
from discord import Option

import asyncio

from inspect import signature
import inspect
from datetime import datetime

import re
import time

import logging
# import logging.handlers
import log_formatter
import os
import json
import sys
import atexit

# import user_api
import bot_plugins

logger = logging.getLogger('helium_logger')

# Decorator for command events execution
def event(name): # Event name
	def decorator(func): # Actual decorator (@)
		def inner(self, *args, **kwargs): # Actual processing
			coros = []
			
			for event in self.events.get(name, []):
				f = event(*args, **kwargs)
				if asyncio.iscoroutine(f):
					coros.append(f)
			
			wrapped = func(self, *args, **kwargs)
			if asyncio.iscoroutine(wrapped):
				coros.append(wrapped)

			async def wait_coros(coros):
				for coro in coros:
					try:
						await coro
					except Exception as e:
						return
			return asyncio.gather(*coros)
			# return wait_coros(coros)

		return inner
	return decorator

class Bot(commands.Bot, *bot_plugins.plugins):
	def __init__(self, admin=None, prefix=None):

		# Settings
		self.settings_path = os.path.abspath('bot_settings')
		self.import_settings()

		atexit.register(self.save_settings)

		# Main bot instance
		intents = discord.Intents().all()
		# TODO - owner_id
		commands.Bot.__init__(self, intents=intents)

		# Plugins:

		# Commands.__init__(self)
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

			self.txt_cmds |= p_txt_cmds

			if events:
				for event, cb in events.items():
					if event in self.events:
						self.events[event].append(cb)
					else:
						self.events[event] = [cb]

		# guild_ids = (e.id for e in self.guilds)
		# for k,v in self.txt_cmds.items():
		# 	self.slash_command(name=v[0], description=k.__doc__, guild_ids=[724303646443044995])(k)

		self.cmds = {k:cmd for cmd, keys in self.txt_cmds.items() for k in keys}
		
		# Prefix
		if not hasattr(self, 'prefix'):
			if prefix == None:
				prefix = '.'
			self.prefix = prefix

		# Admin
		if not hasattr(self, 'admin'):
			if admin is not None:
				self.admin = admin
			else:
				raise ValueError("You must specify the admin's id at least once!")

		self.webhooks = {}
		if not hasattr(self, 'bot_mode'):
			self.bot_mode = []

	@event('on_ready')
	async def on_ready(self):
		logger.info(f'{self.user} is online!, ping: {round(self.latency*1000)}ms')

	async def on_disconnect(self):
		logger.info(f'{self.user} disconnected!')

	@event('on_message')
	async def on_message(self, msg):
		if self.user == msg.author or msg.author.bot:
			return

		if len(msg.embeds) > 0:
			for emb in msg.embeds:
				logger.info(f'{msg.author.display_name}: {emb.to_dict()}')

		if msg.author.id != self.admin and msg.author.id in self.banned_list:
			delay, reason = self.banned_list[msg.author.id]
			if delay is not None and delay < time.time():
				logger.info(f'Unbanned {msg.author.display_name} - time\'s up!')
				del self.banned_list[msg.author.id]
			else:
				await msg.delete()
				logger.info(f'DELETED - {msg.author.display_name}: {msg.content}')
				return

		if msg.content.startswith(self.prefix) and msg.content != self.prefix:
			cmd = self.smart_split(msg.content[len(self.prefix):])

			if cmd[0] in self.cmds:
				logger.info(f'{msg.author.display_name} used the command: {msg.content}')
				f = self.cmds[cmd[0]]

				args = cmd[1:]
				ctx = await self.get_context(msg, cls=CustomContext)
				await self.invoke(ctx)
				sig = signature(f)
				kwargs = {}

				params = iter(sig.parameters.items())
				for k, p in params:
					if p.annotation == ApplicationContext:
						kwargs[k] = ctx

					else:
						if len(args) != 0:
							arg = args.pop(0)
						else:
							arg = None
						try:
							kwargs[k] = await self.format_arg(ctx, arg, p.annotation)
						except MappingError as e:
							await ctx.respond(e)
							return

						# logger.info(await commands.run_converters(ctx, ))
						# logger.info(p.annotation, dir(p.annotation), p.annotation.converter, p.annotation.input_type)
				
				if len(sig.parameters) > 0 and len(args) > 0: # At least one parameter and args not yet parsed
					arg = arg + ' ' + ' '.join(args)
					try:
						kwargs[k] = await self.format_arg(ctx, arg, p.annotation)
					except MappingError as e:
						await ctx.respond(e)
						return
				
				await f(**kwargs)

			else:
				logger.info(f'{msg.author.display_name} used an unknown command: {cmd[0]}')

		else:
			if msg.author.id in self.parrot_list and msg.content != "":
				await msg.channel.send(msg.content, reference=msg)

			logger.info(f'{msg.author.display_name}: {msg.content}')

	async def format_arg(self, ctx, arg, annotation):
		def get_member(ctx, arg):
			if arg is None:
				return None

			m = re.match(r'<@!?(\d{17,19})>', arg)
			if m:
				u_id = int(m.groups()[0])
				return ctx.guild.get_member(u_id)
			
			else:
				logger.warn(f"Can't convert '{arg}' to discord.Member: {arg} - {m}")
				raise MappingError(f"Can't convert '{arg}' to discord.Member")


		format_map = {
			3: lambda ctx, arg: arg, # str
			4: lambda ctx, arg: int(arg), # int
			5: lambda ctx, arg: arg.lower() in ('true','t','1','vrai','v','o','oui'), # bool
			6: commands.MemberConverter().convert, # user / member
			7: commands.GuildChannelConverter().convert, # channel
			8: commands.RoleConverter().convert, # role
			9: commands.ObjectConverter().convert, # mentionable (user / role)
			10: lambda ctx, arg: float(arg), # float
		}

		input_type = annotation.input_type
		hi, lo = annotation.max_value, annotation.min_value
		required = annotation.required
		choices = annotation.choices

		if arg is None:
			if not required:
				return annotation.default
			else:
				raise MappingError(f"Field '{annotation.name}' is required")

		try:
			val = format_map[input_type.value](ctx, arg)
		except Exception as e:
			raise MappingError(str(e))
			# raise MappingError(f"Can't convert '{arg}' to {input_type.name}")

		if asyncio.iscoroutine(val):
			val = await val

		if val is None:
			if not required:
				return annotation.default
			else:
				raise MappingError(f"Field '{annotation.name}' is required")

		if hi is not None and hi < val:
			raise MappingError(f"{val} must be smaller than {hi}")

		if lo is not None and lo > val:
			raise MappingError(f"{val} must be higher than {lo}")

		if len(choices) > 0 and val not in (c.value for c in choices):
			raise MappingError(f"Allowed values are: {'/'.join(map(lambda e: str(e.value), choices))} - (got {val})")

		return val

	@event('on_typing')
	async def on_typing(self, channel, user, when):
		# logger.info(f'{user.display_name} is typing in {channel.name}')
		pass

	@event('on_message_edit')
	async def on_message_edit(self, before, after):
		logger.info(f'Edited in channel {before.channel.name}, guild {before.guild.name}: {before.content} > {after.content}')

	@event('on_message_delete')
	async def on_message_delete(self, msg):
		if msg.channel.id in self.bot_mode and not msg.author.bot:
			return
		if msg.author.id != self.admin and msg.author.id in self.banned_list:
			return
		content = msg.content
		if len(msg.attachments) > 0:
			content += '\n - Attachments: ' + '\n - '.join(map(lambda e: f'{e.filename}: {e.url} / {e.proxy_url}', msg.attachments))
		logger.info(f'A message was deleted in channel {msg.channel.name}, guild {msg.guild.name}: {content}')

	@event('on_reaction_add')
	async def on_reaction_add(self, reaction, user):
		logger.info(f'{user.display_name} added a reaction on: {reaction.message.content}')

	@event('on_reaction_remove')
	async def on_reaction_remove(self, reaction, user):
		logger.info(f'{user.display_name} removed a reaction on: {reaction.message.content}')

	@event('on_member_join')
	async def on_member_join(self, member):
		logger.info(f'{member.display_name} just joined the guild {member.guild.name}!')

	@event('on_reaction_remove')
	async def on_member_remove(self, member):
		logger.info(f'{member.display_name} just left the guild {member.guild.name}!')

	@event('on_member_update')
	async def on_member_update(self, before, after):
		ignore = ['get_relationship']
		keys = ['activities', 'mobile_status', 'display_name', 'nick', 'name', 'pending', 'roles', 'desktop_status', 'web_status', 'status']
		changes = {k:getattr(after,k) for k in keys if getattr(before,k) != getattr(after,k)}
		# logger.info(f'{after.name} just changed his profile on {after.guild.name}, changes:{changes}')

	@event('on_user_update')
	async def on_user_update(self, before, after):
		keys = ['avatar', 'name', 'display_name', 'discriminator']
		changes = {k:getattr(after,k) for k in keys if getattr(before,k) != getattr(after,k)}
		logger.info(f'{after.display_name} just changed his user, changes:{changes}')

	@event('on_guild_role_create')
	async def on_guild_role_create(self, role):
		logger.info(f'New role created in guild {role.guild}: {role.name}')

	@event('on_guild_role_delete')
	async def on_guild_role_delete(self, role):
		logger.info(f'New role removed in guild {role.guild}: {role.name}')

	@event('on_member_ban')
	async def on_member_ban(self, guild, user):
		logger.info(f'User {user.display_name} was banned from the guild {guild.name}')

	@event('on_member_unban')
	async def on_member_unban(self, guild, user):
		logger.info(f'User {user.display_name} was unbanned from the guild {guild.name}')

	@event('on_invite_create')
	async def on_invite_create(self, invite):
		logger.info(f'A new invite has been created for guild {invite.guild.name} by {invite.inviter.display_name}')

	#___________

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

	def smart_split(self, txt, sep=" "):
		out = []
		cur = ''
		in_quotes = False 
		for c in txt:
			if c == '"':
				in_quotes = not in_quotes
			
			elif not in_quotes and c == sep:
				if len(cur) > 0:
					out.append(cur)
					cur = ''
			
			elif c != sep or in_quotes:
				cur += c
		out.append(cur)
		return out

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.save_settings()


class MappingError(Exception):
	pass

class CustomContext(commands.Context):
	"""Mimic a discord.ApplicationContext with a discord.ext.commands.Context"""
	async def respond(self, *args, **kwargs):
		if len(args) == 0 and len(kwargs) == 0:
			return

		if not 'mention_author' in kwargs:
			kwargs['mention_author'] = False
		
		ref = self.message.to_reference(fail_if_not_exists=False)
		
		await self.channel.send(*args, reference=ref, **kwargs)

	async def send(self, *args, **kwargs):
		await self.channel.send(*args, **kwargs)

	@property
	def user(self):
		return self.author

	@property
	def interaction(self):
		return CustomInteraction(self) # Very bad idea but idc


class CustomInteraction:
	def __init__(self, ctx):
		self.ctx = ctx

	@property
	def id(self):
		return self.ctx.message.id

	@property
	def user(self):
		return self.ctx.user

	@property
	def guild(self):
		return self.ctx.guild

	@property
	def message(self):
		return self.ctx.message


if __name__ == "__main__":
	from token_secret import *

	token = helium
	admin = will_i_am_id

	with Bot(admin) as c:
		c.run(token)