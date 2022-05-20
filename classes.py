import asyncio
from pydoc import classname
from discord.ext import commands
from discord.ext.bridge import BridgeApplicationContext, BridgeExtContext

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
		a = self.message.delete()
		b = self.send(*args, **kwargs)
		asyncio.gather(a, b)

class CustomBridgeApplicationContext(BridgeApplicationContext):
	async def replace(self, *args, **kwargs):
		a = self.delete()
		b = self.send(*args, **kwargs)
		asyncio.gather(a, b)
