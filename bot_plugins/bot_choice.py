#Discord_bot.py reaction_choice module

import logging

logger = logging.getLogger('helium_logger')

import discord

class Reaction_Choice:
	"""Reaction choice: choice"""
	def initialize(self):
		txt_cmds = {
			self.choice_create: ['choice_create', 'create_choice'],
			self.choice_modify: ['choice_modify', 'modify_choice'],
			self.choice_add_reaction: ['choice_reaction', 'choice_add_reaction'],
			self.choice_remove_reaction: ['choice_del_reaction', 'choice_remove_reaction', 'choice_delete_reaction'],
			self.choice_delete: ['choice_delete', 'delete_choice']
		}

		events = {
			'on_reaction_add': self.check_reaction_add,
			'on_reaction_remove': self.check_reaction_remove
		}

		if not hasattr(self, 'choices_data'):
			self.choices_data = {}

		return txt_cmds, events

	@discord.option(
		"title",
		description="The title"
	)
	@discord.option(
		"description",
		description="The description"
	)
	@discord.option(
		"color",
		description="The color, in hex"
	)
	async def choice_create(self, 
		ctx,
		title : str,
		desc : str,
		col : str = None
		):
		"Create a new reaction choice"

		if not self.is_admin(ctx.author):
			await ctx.respond('This command is for admins only!')
			return

		if title in (data['title'] for data in self.choices_data.values()):
			await ctx.respond(f"A reaction choice with title '{title}' already exists! Please delete the previous one or use a different title.")
			return

		if col is None:
			col = 0x0000FF
		else:
			try:
				col = int(col, 16)
			except ValueError:
				await ctx.respond(f'{col} is an invalid hex color!')
				return

		data = {
			'guild': ctx.guild.id,
			'channel': ctx.channel.id,
			'title': title,
			'description': desc,
			'color': col,
			'reactions': []
		}

		emb, emojis = self.format_reaction(data)

		msg = await ctx.send(embed=emb)
		m_id = msg.id
		data['id'] = m_id

		self.choices_data[m_id] = data

		await ctx.hidden('Done', delete_after=5*60) # 5 mins

	@discord.option(
		"title",
		description="The title of the choice to modify"
	)
	@discord.option(
		"description",
		description="The new description"
	)
	@discord.option(
		"color",
		description="The new color, in hex"
	)
	async def choice_modify(self, 
		ctx,
		title : str,
		desc : str = None,
		col : str = None
		):
		"Modify a reaction choice"

		if not self.is_admin(ctx.author):
			await ctx.respond('This command is for admins only!')
			return

		found = False
		for id, data in self.choices_data.items():
			if title == data['title']:
				found = True
				break

		if not found:
			await ctx.respond(f"Reaction choice '{title}' doesn't exists yet!")
			return

		if desc is not None:
			data['description'] = desc

		if col is not None:
			try:
				col = int(col, 16)
			except ValueError:
				await ctx.respond(f'{col} is an invalid hex color!')
				return

			data['color'] = col

		emb, emojis = self.format_reaction(data)
		try:
			msg = await self.get_message_from_data(data)
			await msg.edit(embed=emb)
		except discord.NotFound:
			await ctx.respond('Choice was not found!')
			logger.warning(f'Msg id {data["id"]} was not found!')
		self.choices_data[data['id']] = data

		await ctx.hidden('Done', delete_after=5*60) # 5 mins


	@discord.option(
		"title",
		description="The title of the choice to modify"
	)
	@discord.option(
		"emoji",
		description="The emoji reaction"
	)
	@discord.option(
		"role",
		description="The role associated"
	)
	@discord.option(
		"desc",
		description="The description for that choice"
	)
	async def choice_add_reaction(self, 
		ctx,
		title : str,
		emoji : str,
		role : discord.Role,
		desc : str = None,
		):
		"Add a reaction to a reaction choice"

		if not self.is_admin(ctx.author):
			await ctx.respond('This command is for admins only!')
			return

		found = False
		for id, data in self.choices_data.items():
			if title == data['title']:
				found = True
				break

		if not found:
			await ctx.respond(f"Reaction choice '{title}' doesn't exists yet!")
			return

		if desc is None:
			desc = role.name

		if role.id in (react['role'] for react in data['reactions']):
			await ctx.respond(f"There is already a reaction with that role!")
			return

		reaction = {
			'emoji': emoji,
			'description': desc,
			'role': role.id
		}

		# Fetch message object
		try:
			msg = await self.get_message_from_data(data)
		except discord.NotFound:
			await ctx.respond(f'The choice was not found!')
			logger.warning(f'Msg id {data["id"]} was not found!')
			return

		# Update embed content
		emb, emojis = self.format_reaction(data)
		try:
			await msg.edit(embed=emb)
		except discord.Forbidden:
			await ctx.respond('I don\'t have the permissions to edit the message!')

		# Add the emoji
		try:
			await msg.add_reaction(emoji)
		except discord.Forbidden:
			await ctx.respond('I don\'t have the permissions to add an emoji!')
			return
		except discord.InvalidArgument:
			await ctx.respond(f'{emoji} is an invalid emoji!')
			return

		data['reactions'].append(reaction)
		self.choices_data[data['id']] = data

		await ctx.hidden('Done', delete_after=5*60) # 5 mins


	@discord.option(
		"title",
		description="The title of the choice to modify"
	)
	@discord.option(
		"role",
		description="The role associated"
	)
	async def choice_remove_reaction(self, 
		ctx,
		title : str,
		role : discord.Role
		):
		"Remove a reaction to a reaction choice"

		if not self.is_admin(ctx.author):
			await ctx.respond('This command is for admins only!')
			return

		found = False
		for id, data in self.choices_data.items():
			if title == data['title']:
				found = True
				break

		if not found:
			await ctx.respond(f"Reaction choice '{title}' doesn't exists yet!")
			return

		found = False
		for react in data['reactions']:
			if role.id == react['role']:
				found = True
				data['reactions'].remove(react)
				self.choices_data[data['id']] = data
				break
		
		if not found:
			await ctx.respond(f"Role '{role.name}' hasn't been added on reaction with title '{title}'!")
			return
		
		# TODO

		await ctx.hidden('Done', delete_after=5*60) # 5 mins


	@discord.option(
		"title",
		description="The title of the choice to delete"
	)
	async def choice_delete(self, 
		ctx,
		title : str
		):
		"Delete a reaction choice"

		if not self.is_admin(ctx.author):
			await ctx.respond('This command is for admins only!')
			return

		found = False
		for id, data in self.choices_data.items():
			if title == data['title']:
				found = True
				break

		if not found:
			await ctx.respond(f"Reaction choice '{title}' doesn't exists yet!")
			return

		m_id = data['id']
		# msg = find msg from id
		try:
			msg = await self.get_message_from_data(data)
			await msg.delete() # TODO - Errors handling
		except discord.NotFound:
			await ctx.respond('The choice was not found!')
			logger.warning(f'Msg id {id} raised NotFound exception on choice_delete')
		del self.choices_data[m_id]
		
		await ctx.hidden('Done', delete_after=5*60) # 5 mins

	async def check_reaction(self, add, reaction, user):
		if reaction.message.author.bot: # Bot shouldn't get perms
			return
		m_id = reaction.message.id
		if m_id in self.choices_data:
			data = self.choices_data[m_id]
			emoji = reaction.emoji
			for react_data in data['reactions']:
				if emoji == react_data['emoji']:
					role_id = react_data['role']
					if add is True:
						await user.add_roles(discord.Object(id=role_id))
					else:
						await user.remove_roles(discord.Object(id=role_id))
					return

			# Unknown emoji
			await reaction.remove()

	async def check_reaction_add(self, reaction, user):
		return await self.check_reaction(True, reaction, user)
	
	async def check_reaction_remove(self, reaction, user):
		return await self.check_reaction(False, reaction, user)
	
	def format_reaction(self, reaction):
		desc = reaction['description']
		emojis = []

		for role_data in reaction['reactions']:
			desc += f"\n{role_data['emoji']}: {role_data['description']}"
			emojis.append(role_data['emoji'])

		emb = {
			'type': 'rich',
			'title': reaction['title'],
			'description': desc,
			'color': reaction['color']
		}

		emb = discord.Embed.from_dict(emb)

		return emb, emojis

	async def get_message_from_data(self, data):
		msg = self.get_message(data['id']) # Cache
		if msg is not None:
			return msg
		else:
			guild = self.get_guild(data['guild']) # Cache
			if guild is not None:
				channel = guild.get_channel(data['channel']) # Cache

			if channel is None:
				# No need to get guild first
				channel = await guild.fetch_channel(data['channel']) # API

			msg = await channel.fetch_message(data['id']) # API
			return msg


module_class = Reaction_Choice