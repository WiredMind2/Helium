#Discord_bot.py translate module

import discord
from discord.commands.context import ApplicationContext
from discord.commands import Option
import logging
logger = logging.getLogger('helium_logger')

try:
	from googletrans import Translator, LANGUAGES
except ImportError:
	logger.info('googletrans module not found!')
	exit()

class Translate:
	"""Translate: trans"""
	def initialize(self):
		txt_cmds = {
			self.translate: ['translate', 'uh', 'huh']
		}
		self.translator = Translator()

		return txt_cmds

	async def translate(self, 
		ctx : ApplicationContext,
		txt : Option(
			str,
			"The text you want to translate",
			name="msg",
			default=""),
		):
		"Translate a message or a text:\n > .uh J'aime les pâtes!"

		msg = ctx.interaction.message
		if txt != "":
			orig = txt
		elif msg.reference is not None and msg.reference.resolved is not None and hasattr(msg.reference.resolved, 'content') and msg.reference.resolved.content is not None:
			orig = msg.reference.resolved.content
		else:
			await ctx.respond('You must specify a text or a message to translate!')

		logger.info(f'Translating {orig}')
		try:
			trans = self.translator.translate(text=orig)
		except Exception as e:
			logger.warn(f'Error while translating {orig}: {e}')
			await ctx.respond(f'Internal error while translating:sob:')
		else:
			await ctx.respond(f'From {LANGUAGES[trans.src].capitalize()}: {trans.text}')

module_class = Translate
