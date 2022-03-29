#Discord_bot.py random module

import discord
from discord import ApplicationContext, Option
import logging
logger = logging.getLogger('helium_logger')

class Bot_mode:
	"""Bot mode: bot"""
	def initialize(self):
		txt_cmds = {
			self.set_bot_mode: ['bot', 'botmode', 'set_bot', 'set_botmode'],
			self.swap_user: ['ghost', 'imitate', 'swap'],
		}

		# for self.swap_user():
		if not hasattr(self, 'swaped_users'):
			self.swaped_users = {}

		return txt_cmds

	async def set_bot_mode(self, 
		ctx : ApplicationContext,
		mode : Option(
			str,
			"Action",
			name="action",
			choices=["on", "off", "status"],
			required=True),
		):
		"Bot mode: everyone get a 'bot' tag next to their name:\n > .bot on/off/status"

		c_id = ctx.channel.id

		if mode == 'on':
			mode = True

		elif mode == 'off':
			mode = False

		elif mode == 'status':
			mode = c_id in self.bot_mode
			status = "ENABLED" if mode else "DISABLED"
			await ctx.respond(f'Bot mode: **{status}**')
			return

		else:
			await ctx.respond(f'Invalid action: {mode} (on/off/status)!')
			return

		if mode:
			webhook = await self.get_webhook(ctx.channel)
			perms = ctx.channel.permissions_for(ctx.guild.me)

			if webhook is None or not perms.manage_webhooks or not perms.manage_messages:
				await ctx.respond("I need the 'Manage Webhooks' and 'Manage Messages' permissions to enable bot mode!")
				mode = False

			elif c_id not in self.bot_mode:
				self.bot_mode.append(c_id)
		else:
			if c_id in self.bot_mode:
				self.bot_mode.remove(c_id)

		if mode:
			await ctx.respond('Bot mode: **ENABLED**')
		else:
			await ctx.respond('Bot mode: **DISABLED**')

	async def swap_user(self, 
		ctx : ApplicationContext,
		user : Option(
			discord.Member,
			"User to swap with",
			name="user",
			default=None)
		):
		"While in bot mode, allow you to talk as someone else:\n > .swap @user"

		if ctx.channel.id not in self.bot_mode:
			await ctx.respond('You must activate bot mode first!')
			return
		if ctx.author.bot:
			try:
				await msg.delete()
			except:
				pass

		if user is None:
			del self.swaped_users[ctx.author.id]
			return

		self.swaped_users[ctx.author.id] = user

module_class = Bot_mode