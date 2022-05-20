#Discord_bot.py misc module

import discord

import asyncio
import random
import logging
logger = logging.getLogger('helium_logger')

class Misc:
	"""Misc: misc"""
	def initialize(self):
		txt_cmds = {
			self.help: ['doc', 'docs'],#, 'help'],
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

	@discord.option(
		'user',
		description="The user to salute",
	)
	async def salute(self, 
		ctx,
		user : discord.Member = None
		):
		"Helium is a very polite bot: \n .hi @Helium"
		if user is None:
			user = ctx.author
		txts = ['Hey {user}!', 'Hello {user}!', 'Good day to you, {user}!', 'Greetings, {user}, how are you today?']
		await ctx.respond(random.choice(txts).format(user=user.display_name))

	@discord.option(
		'content',
		decription="The message to repeat"
	)
	async def say(self, 
		ctx,
		content : str
		):
		"Will repeat the content of your message:\n > .say I like pasta!"
		if len(content) == 0:
			await ctx.respond('What am I supposed to say?')
			return

		replacements = {
			'@here': '@​here',
			'@everyone': '@​everyone',
			'fuck': 'f***'
		}
		for txt, rep in replacements.items():
			content = content.replace(txt, rep)

		await ctx.replace(content)

	@discord.option(
		'amount',
		description="Number of messages to send"
	)
	@discord.option(
		'content',
		description="Message to send",
	)
	@discord.option(
		'delay',
		description="Delay between messages"
	)
	@discord.option(
		'counter',
		description="Add a number before each message"
	)
	async def spam(self, 
		ctx,
		amount : int,
		content : str,
		delay : int = 1,
		log_count : bool = True
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

	@discord.option(
		'user',
		description="User to ping"
	)
	async def ping(self, 
		ctx,
		user : discord.User = None
		):
		"Ping the bot:\n > .ping\nAlso works like .mention:\n > .ping helium"
		if user is not None:
			return await self.mention(ctx, user)
		await ctx.respond(f"Pong: {round(self.latency*1000)}ms")

	@discord.option(
		'cat',
		description="A category or a command",
	)
	async def help(self, 
		ctx,
		cat : str = None,
		):
		"Show Helium's help:\n > .help (cat)"

		if cat is None: # Main page
			cats = []
			i = 0
			for p in self.plugins:
				try:
					name, arg = p.__doc__.split(':')
					name, arg = name.strip(), arg.strip()
					if name.startswith('(Admin)'):
						continue

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
					i += 1
				except Exception as e:
					logger.warn(f'Error on help, module {p}: {e}')
					pass

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

		# Plugin help page
		p = filter(lambda p: p.__doc__.split(':')[1].strip() == cat, self.plugins)
		p = next(p, None)

		if p is None: # Cat not found
			emb = {
				"type": "rich",
				"title": f"Helium's help - {name}",
				"description": f"Module '{name}' is not found!",
				"color": 0x00FFFF
			}

			emb = discord.Embed.from_dict(emb)
			await ctx.respond(embed=emb)
			return


		txt_cmds = p.initialize(self)
		if isinstance(txt_cmds, tuple):
			txt_cmds = txt_cmds[0]
		docs = []
		for f, keys in txt_cmds.items():
			if f.__doc__ is not None and '(admin only!)' not in f.__doc__:
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

	@discord.option(
		'user',
		description="User to ping",
	)
	async def mention(self, 
		ctx,
		user : discord.User
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
		try:
			ctx.replace(user.mention)
		except discord.NotFound as e:
			logger.info(f'Error on .say: {e}')

	@discord.option(
		'user',
		description="The target",
	)
	@discord.option(
		'action',
		description="Start or stop",
		choices=["start", "stop"],
	)
	async def repeat(self, 
		ctx,
		user : discord.Member,
		action : str = None
		):
		"Act like a parrot:\n > .repeat (start/stop/?) @user"

		if user.id == ctx.author.id and not user.top_role.permissions.manage_messages:
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

	@discord.option(
		'max_count',
		description="Count up to ...",
	)
	async def count(self, 
		ctx,
		max_count : int
		):

		for i in range(1, max_count+1):
			await ctx.send(f'{i}/{max_count}')

module_class = Misc