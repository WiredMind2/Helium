#Discord_bot.py reaction_choice module

import asyncio
import logging
logger = logging.getLogger('helium_logger')

import discord
from discord import ApplicationContext, Option

class Reaction_Choice:
	def initialize(self):
		txt_cmds = {
			self.choice_create: ['choice_create', 'create_choice'],
			self.choice_modify: ['choice_modify', 'modify_choice'],
			self.choice_add_reaction: ['choice_reaction', 'choice_add_reaction'],
			self.choice_remove_reaction: ['choice_del_reaction', 'choice_remove_reaction', 'choice_delete_reaction'],
			self.choice_delete: ['choice_delete', 'delete_choice']
		}

		events = {
			'on_reaction_add': self.check_reaction
		}

		if not hasattr(self, 'choices_data'):
			self.choices_data = {}

		return txt_cmds, events

	def choice_create(self, 
		ctx : ApplicationContext,
		title : Option(
			str,
			"The title",
			name="title"),
		desc : Option(
			str,
			"The description",
			name="description"),
		col : Option(
			str,
			"The color, in hex",
			name="color")
		):
		"Create a new reaction choice"

		if ctx.author != self.admin:
			ctx.respond('This command is for admins only!')
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
			'guild': ctx.guild,
			'channel': ctx.channel,
			'title': title,
			'description': desc,
			'color': col,
			'reactions': []
		}

		emb, emojis = self.format_reaction(data)

		m_id = ctx.send(emb)
		data['id'] = m_id

		self.choices_data[m_id] = data

	def choice_modify(self, 
		ctx : ApplicationContext,
		title : Option(
			str,
			"The title of the choice to modify",
			name="title"),
		desc : Option(
			str,
			"The new description",
			name="description",
			default=None)=None,
		col : Option(
			str,
			"The new color, in hex",
			name="color",
			default=None)=None
		):
		"Modify a reaction choice"

		if ctx.author != self.admin:
			ctx.respond('This command is for admins only!')
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
			data['desc'] = desc

		if col is not None:
			try:
				col = int(col, 16)
			except ValueError:
				ctx.respond(f'{col} is an invalid hex color!')
				return

			data['col'] = col

		emb, emojis = self.format_reaction(data)
		m_id = data['id']
		# msg = find msg from id
		# await msg.modify(embed=emb)

		self.choices_data[data['id']] = data

	def choice_add_reaction(self, 
		ctx : ApplicationContext,
		title : Option(
			str,
			"The title of the choice to modify",
			name="title"),
		emoji : Option(
			str,
			"The emoji reaction",
			name="emoji"),
		role : Option(
			discord.Role,
			"The role associated",
			name="role"),
		desc : Option(
			str,
			"The description for that choice",
			name="description",
			default=None)=None,
		):
		"Add a reaction to a reaction choice"

		if ctx.author != self.admin:
			ctx.respond('This command is for admins only!')
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

		if role in (react['role'] for react in data['reactions']):
			await ctx.respond(f"There is already a reaction with role '{role}'!")
			return

		reaction = {
			'emoji': emoji,
			'desc': desc,
			'role': role
		}

		data['reactions'].append(reaction)
		self.choices_data[m_id] = data

	def choice_remove_reaction(self, 
		ctx : ApplicationContext,
		title : Option(
			str,
			"The title of the choice to modify",
			name="title"),
		role : Option(
			discord.Role,
			"The role associated",
			name="role")
		):
		"Remove a reaction to a reaction choice"

		if ctx.author != self.admin:
			ctx.respond('This command is for admins only!')
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
			if role == react['role']:
				found = True
				data['reactions'].remove(react)
				self.choices_data[data['id']] = data
				break
		
		if not found:
			await ctx.respond(f"Role '{role.name}' hasn't been added on reaction with title '{title}'!")
			return

	def choice_delete(self, 
		ctx : ApplicationContext,
		title : Option(
			str,
			"The title of the choice to delete",
			name="title")
		):
		"Delete a reaction choice"

		if ctx.author != self.admin:
			ctx.respond('This command is for admins only!')
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
		await msg.delete() # TODO - Errors handling
		del self.choices_data[m_id]

	def check_reaction(self, reaction, user):
		m_id = reaction.msg.id
		if m_id in self.choices_data:
			data = self.choices_data[m_id]
			emoji = reaction.emoji
			for react_data in data:
				if emoji == react_data['emoji']:
					await user.add_roles(react_data['role'])
					return

			# Unknown emoji
			await reaction.delete()

	def format_reaction(self, reaction):
		desc = reaction['desc']
		emojis = []

		for role_data in reaction['reactions']:
			desc += f"\n{role_data['emoji']}: {role_data['desc']}"
			emojis.append(role_data['emoji'])
		
		emb = {
			'type': 'rich',
			'title': reaction['title'],
			'description': desc,
			'color': reaction['col']
		}

		return emb, emojis