#Discord_bot.py reaction_choice module

import asyncio
import logging
logger = logging.getLogger('helium_logger')

import discord
from discord import ApplicationContext, Option

import random
from datetime import datetime

class Levels:
	def initialize(self):
		txt_cmds = {
			self.add_xp: ['xp', 'give_xp', 'add_xp'],
			self.reset_xp: ['reset_xp']
		}

		events = {
			'on_message': self.message_xp_level
		}

		self.msg_xp = (15, 30) # (min, max)
		self.xp_multiplier = 1

		self.last_minute_ids = set()
		self.last_update_minute = datetime.now().time().minute

		if not hasattr(self, 'user_levels'):
			self.user_levels = {}

		return txt_cmds, events

	async def message_xp_level(self, msg):
		author_id = msg.author.id

		minute = datetime.now().time().minute
		if minute != self.last_update_minute: # Reset talk cooldown
			self.last_update_minute = minute
			self.last_minute_ids.clear()

		if author_id not in self.last_minute_ids: # Haven't spoken yet in the last minute
			self.last_minute_ids.add(author_id)

			xp = random.randint(*self.msg_xp) * self.xp_multiplier
			if author_id in self.user_levels:
				self.user_levels[author_id] += xp
			else:
				self.user_levels[author_id] = xp

	async def add_xp(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The member to give xp to",
			name="member"),
		amount : Option(
			int,
			"The amount of xp to give",
			name="amount")
		):
		"Gives xp to a member (negative amount to remove)"

		if ctx.author.id != self.admin:
			await ctx.respond('This command is for admins only!')

		if target.id in self.user_levels:
			self.user_levels[target.id] += amount
		else:
			self.user_levels[target.id] = amount

		if self.user_levels[target.id] <= 0:
			del self.user_levels[target.id]
			await ctx.respond(f"Xp of member '{target.display_name}' has been reset!")
		else:
			await ctx.respond(f"Xp of member '{target.display_name}' is now {self.user_levels[target.id]} xp")

	async def reset_xp(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The member to reset the xp",
			name="member"),
		):
		"Reset the xp of a member"

		if ctx.author.id != self.admin:
			await ctx.respond('This command is for admins only!')
			return

		if target.id in self.user_levels:
			del self.user_levels[target.id]
			await ctx.respond(f"Resetted xp of member {target.display_name}")
		else:
			await ctx.respond(f"Member {target.display_name} has no xp!")

module_class = Levels