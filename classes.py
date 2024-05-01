import asyncio
import logging

from discord.ext import commands
from discord.ext.bridge import BridgeApplicationContext, BridgeExtContext, BridgeContext

logger = logging.getLogger('helium_logger')

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

class CustomBridgeExtContext(BridgeExtContext):
	async def replace(self, *args, **kwargs):
		# Replace the command msg with the response
		a = self.message.delete()
		b = self.send(*args, **kwargs)
		asyncio.gather(a, b)
	
	async def hidden(self, *args, **kwargs):
		# Respond with a temporary message and set timeout on command
		if 'delete_after' not in kwargs:
			kwargs['delete_after'] = 60*15 # 15 mins
		
		a = self.respond(*args, **kwargs)
		b = self.message.edit(delete_after=kwargs['delete_after'])
		asyncio.gather(a, b)

class CustomBridgeApplicationContext(BridgeApplicationContext):
	async def replace(self, *args, **kwargs):
		# Delete the interaction and send the response
		a = self.delete()
		b = self.send(*args, **kwargs)
		asyncio.gather(a, b)
	
	async def hidden(self, *args, **kwargs):
		# Respond with a ephemeral message
		if 'delete_after' not in kwargs:
			kwargs['delete_after'] = 60*15 # 15 mins
		kwargs['ephemeral'] = True

		await self.respond(*args, **kwargs)

def custom_check(predicate, func=None):
	# Custom commands.check implementation
	# commands.check
	def decorator(func):
		async def wrapper(*args, **kwargs):
			if 'ctx' in kwargs:
				ctx = kwargs.get(ctx) # No need for type checking, we won't find anything else anyway
			elif len(args) == 0:
				logger.error(f'Function {func} was ran with no args? (ctx not found)')
				return
			elif len(args) == 1 and isinstance(args[0], BridgeContext):
				# Function (ctx, *args, **kwargs)
				ctx = args[0]
			elif isinstance(args[1], BridgeContext):
				# Method (self, ctx, *args, **kwargs)
				ctx = args[1]
			else:
				logger.error(f'Ctx not found for function {func}, args {args}!')
				return

			if predicate(ctx):
				if asyncio.iscoroutinefunction(func):
					return await func(*args, **kwargs)
				else:
					return func(*args, **kwargs)
		return wrapper
	if func is None:
		return decorator
	else:
		return decorator(func)
