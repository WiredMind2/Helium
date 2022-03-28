#Discord_bot.py misc module

import discord
from discord import ApplicationContext, Option

import asyncio
import random
import logging
logger = logging.getLogger(__name__)

class Misc:
	"""Misc: misc"""
	def initialize(self):
		txt_cmds = {
			self.help: ['doc', 'docs', 'help'],
			self.salute: ['hello', 'hey', 'hi', 'salute', 'test'],
			self.say: ['say'],
			self.repeat: ['parrot', 'repeat'],
			self.mention: ['mention'], #, 'find', 'match', 'search'],
			self.ping: ['ping'],
			self.spam: ['spam'],
			self.count: ['count']
		}

		# for self.repeat():
		if not hasattr(self, 'parrot_list'):
			self.parrot_list = []

		return txt_cmds

	async def salute(self, 
		ctx : ApplicationContext,
		user : Option(
			discord.Member,
			"The user to salute", 
			name="user",
			default=None)
		):
		"Helium is a very polite bot: \n .hi @Helium"
		if user is None:
			user = ctx.user
		txts = ['Hey {user}!', 'Hello {user}!', 'Good day to you, {user}!', 'Greetings, {user}, how are you today?']
		await ctx.respond(random.choice(txts).format(user=user.display_name))

	async def say(self, 
		ctx : ApplicationContext,
		content : Option(
			str,
			"The message to repeat", 
			name="message")
		):
		"Will repeat the content of your message:\n > .say I like pasta!"
		if len(content) == 0:
			await msg.channel.send('What am I supposed to say?')
			return
		replacements = {
			'@here': '@​here',
			'@everyone': '@​everyone',
			'fuck': 'f***'
		}
		for txt, rep in replacements.items():
			content = content.replace(txt, rep)
		a = ctx.send(content)
		b = ctx.message.delete()
		try:
			await asyncio.gather(a, b)
		except discord.NotFound:
			pass

	async def spam(self, 
		ctx : ApplicationContext,
		amount : Option(
			int,
			"Number of messages to send", 
			name="amount"),
		content : Option(
			str,
			"Message to send", 
			name="message"),
		delay : Option(
			int,
			"Delay between messages", 
			name="delay", 
			default=1),
		log_count : Option(
			bool,
			"Log the count of each message",
			name="log_count",
			default=True)
		):
		"Spam a message:\n > .spam 20 I like pasta!"
		if len(content) == 0:
			await ctx.respond('You need to specify a message to spam!')
			return

		replacements = {
			'@here': '@​here',
			'@everyone': '@​everyone',
			'fuck': 'f***'
		}
		for txt, rep in replacements.items():
			content = content.replace(txt, rep)

		pre = ''

		for i in range(amount):
			if log_count:
				pre = f'{i+1}: '
			try:
				await ctx.send(f'{pre}{content}')
			except Exception as e:
				logger.warn(f'Error while spamming (iter n{i+1}): {e}')
			await asyncio.sleep(delay)

	async def ping(self, 
		ctx : ApplicationContext,
		user : Option(
			discord.User,
			"User to ping",
			name="user",
			default=None) = None
		):
		"Ping the bot:\n > .ping\nAlso works like .mention:\n > .ping helium"
		if user is not None:
			return await self.mention(ctx, user)
		await ctx.respond(f"Pong: {round(self.latency*1000)}ms")

	async def help(self, 
		ctx : ApplicationContext,
		cat : Option(
			str,
			"A category or a command", 
			name="cat",
			default=None) = None,
		):
		"Show Helium's help:\n > .help (cat)"

		if cat is None:
			cats = []
			for i, p in enumerate(self.plugins):
				name, arg = p.__doc__.split(':')
				name, arg = name.strip(), arg.strip()
				
				count = len(p.initialize(self))

				field = {
					'name': name,
					'value': f'{count} commands:\n > .help {arg}\n',
					'inline': True
				}
				cats.append(field)

				if i%2 == 1:
					cats.append({
						'name': '​',
						'value': '​',
						'inline': True
					})

			emb = {
				"type": "rich",
				"title": "Helium's help",
				"description": "Please choose a category:",
				"color": 0x00FFFF,
				"fields": cats
			}

			emb = discord.Embed.from_dict(emb)
			await ctx.respond(embed=emb)
			return

		p = filter(lambda p: p.__doc__.split(':')[1].strip() == cat, self.plugins)
		p = next(p)

		txt_cmds = p.initialize(self)
		docs = []
		for f, keys in txt_cmds.items():
			if f.__doc__ is not None:
				field = {
					'name': ' | '.join(map(lambda e: '.' + e, keys)),
					'value': f.__doc__
				}
				docs.append(field)

		name, arg = p.__doc__.split(':')
		name, arg = name.strip(), arg.strip()

		emb = {
			"type": "rich",
			"title": f"Helium's help - {name}",
			"description": f"All commands available with Helium's {name} module:",
			"color": 0x00FFFF,
			"fields": docs
		}

		emb = discord.Embed.from_dict(emb)
		await ctx.respond(embed=emb)

	async def mention(self, 
		ctx : ApplicationContext,
		user : Option(
			discord.User,
			"User to ping",
			name="user")
		):
		"Ping somebody:\n > .ping helium"

		# User mention regex: r'<@&(\d{17,19})>'
		# search = args[0].lower()
		# match = discord.utils.find(lambda e: search in e.name.lower() and hasattr(e, 'mention'), (e for sub in (msg.guild.members, msg.guild.roles, msg.guild.channels) for e in sub))
		#
		# if match is None:
		# 	await msg.channel.send(f'Nothing found for: {args[0]}!')
		# 	return

		# if hasattr(match, 'position') and match.position == 0:
		# 	await msg.channel.send("You can ping @​everyone yourself! (I don't want any troubles)")
		# 	return 
		a = ctx.send(user.mention)
		b = ctx.message.delete()
		try:
			await asyncio.gather(a, b)
		except discord.NotFound as e:
			logger.info(f'Error on .say: {e}')

	async def repeat(self, 
		ctx : ApplicationContext,
		user : Option(
			discord.Member,
			"The target",
			name="user"),
		action : Option(
			str,
			"Action",
			name="action",
			choices=["start", "stop", None],
			default=None)
		):
		"Act like a parrot:\n > .repeat (start/stop/?) @user"

		if user.id == ctx.user.id and not user.top_role.permissions.manage_messages:
			await ctx.respond("You can't do this yourself!")
			return

		force = False
		add = None

		if action == "start":
			force = True
			add = True
		elif action == "stop":
			force = True
			add = False

		if (force and add) or user.id not in self.parrot_list:
			self.parrot_list.append(user.id)
			await ctx.respond(f"I will now repeat {user.display_name}!")
			return
		if (force and not add) or user.id in self.parrot_list:
			self.parrot_list.remove(user.id)
			await ctx.respond(f"I will stop to repeat {user.display_name}")
			return

	async def count(self, 
		ctx : ApplicationContext,
		max_count : Option(
			int,
			"Count up to ...",
			name="count")
		):

		for i in range(1, max_count+1):
			await ctx.send(f'{i}/{max_count}')

module_class = Misc
