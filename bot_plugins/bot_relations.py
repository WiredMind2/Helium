#Discord_bot.py relations module

import discord
from discord.commands import Option
import logging
logger = logging.getLogger('helium_logger')

class Relations:
	"""Relations: rels"""
	def initialize(self):
		txt_cmds = {
			self.marry: ['marry'],
			self.married: ['married', 'marriedlist'],
			self.dump: ['dump', 'divorce'],
			self.marry_all: ['marry_all'],
			self.adopt: ['adopt'],
			self.adopted: ['adopted'],
			self.emancipate: ['emancipate', 'abandon']
			# self.sibling: ['sibling'],
		}

		# for self.mary():
		if not hasattr(self, 'married_users'):
			self.married_users = {}
		if not hasattr(self, 'marry_requests'):
			self.marry_requests = {}

		# for self.adopt():
		if not hasattr(self, 'adopt_requests'):
			self.adopt_requests = {}
		if not hasattr(self, 'adopted_users'):
			self.adopted_users = {}

		return txt_cmds

	async def marry(self, 
		ctx,
		user : Option(
			discord.Member,
			"Your groom / bride",
			name="user",
			required=True),
		text : Option(
			str,
			"Your declaration of love",
			name="declaration",
			default="") = ""
		):
		"Send or accept a request to mary somebody"

		author = ctx.author
		author_id = author.id
		user_id = user.id

		self.marry_requests = {int(k):v for k,v in self.marry_requests.items()} # Json can't convert keys back to int ?
		self.married_users = {int(k):v for k,v in self.married_users.items()}


		if user_id in self.married_users.get(author_id, []):
			await ctx.respond(f'You two are already married!')
			return

		if user_id == author_id:
			await ctx.respond("You can't marry yourself...")
			return

		if user.bot:
			await ctx.respond("You can't marry a bot!")
			return

		if author.bot:
			await ctx.respond("A bot can't get married!")
			return


		if author_id not in self.marry_requests:
			self.marry_requests[author_id] = []

		if user_id in self.marry_requests[author_id]: # Received a request from user
			if author_id not in self.married_users:
				self.married_users[author_id] = [user_id]
			else:
				self.married_users[author_id].append(user_id)

			if user_id not in self.married_users:
				self.married_users[user_id] = [author_id]
			else:
				self.married_users[user_id].append(author_id)

			self.marry_requests[author_id].remove(user_id)

			if author_id in self.marry_requests.get(user_id, []):
				# Shouldn't happen, but whatever
				self.marry_requests[user_id].remove(author_id)

			await ctx.respond(f'Congratulations! {author.mention} and {user.mention} are now married!')

		else:
			if user_id not in self.marry_requests: # Hasn't received any request yet
				self.marry_requests[user_id] = []

			if author_id in self.marry_requests[user_id]: # Has already received a request
				desc = f'{user.mention}: {author.mention} has proposed (again) to you.'

			else: # Hasn't received a request from author
				self.marry_requests[user_id].append(author_id)
				desc = f'{user.mention}: {author.mention} has proposed to you.'

			emb = {
				"title": "Marriage Proposal",
				"description": desc,
				"color": 0xea9ab,
				"footer": {
					"text": f"Use .marry @{author.display_name} to accept!"
				}
			}

			await ctx.respond(embed=discord.Embed.from_dict(emb))

		self.save_settings()

	async def married(self, 
		ctx
		):
		"List all married members"

		guild = ctx.guild

		emb = {
			"title": f"Relations on the {guild.name} server:",
			"color": 0xea9ab,
			"fields": [],
			"footer": {
				"text": "Use .marry @user to marry someone!"
			}
		}

		fields = []

		data = sorted(self.married_users.items(), key=lambda e: len(e[1]), reverse=True)

		for i, tmp in enumerate(data):
			groom_id, brides = tmp
			groom = guild.get_member(int(groom_id))

			if groom is not None:
				txt = ''
				for bride_id in brides:
					bride = guild.get_member(bride_id)
					if bride is not None:
						txt += f"- {bride.display_name}\n"

				field = {
					"name": f'{i+1}: {groom.display_name} is married with:',
					"value": txt,
					"inline": False
				}

				if txt != '': # At least one bride in the guild
					fields.append(field)

		if len(fields) > 0:
			emb['fields'] = fields
			await ctx.respond(embed=discord.Embed.from_dict(emb))
		else:
			await ctx.respond('There are no couple on this guild!')

	async def dump(self, 
		ctx,
		user : Option(
			discord.Member,
			"The one you want to dump",
			name="dumped",
			required=True),
		):
		"Wanna be single again?"

		author = ctx.author
		author_id = author.id
		user_id = user.id

		self.married_users = {int(k):v for k,v in self.married_users.items()}

		if author_id == user_id:
			await ctx.respond(f"You can't dump yourself!")

		if user_id in self.married_users[author_id]:
			self.married_users[author_id].remove(user_id)
			self.married_users[user_id].remove(author_id)

			await ctx.respond(f'{author.mention} dumped {user.mention}!')

		else:
			await ctx.respond(f"You're not married with {user.display_name}!")

	async def marry_all(self,
		ctx,
		target : Option(
			discord.Member,
			"Who should be married with everybody else",
			name="target",
			required=True),
		):
		"Wanna marry @everyone? (Admin only)"

		if not self.is_admin(ctx.author):
			await ctx.respond('Only the bot\'s admin can use this command!')

		self.marry_requests = {int(k):v for k,v in self.marry_requests.items()} # Json can't convert keys back to int ?
		self.married_users = {int(k):v for k,v in self.married_users.items()}
		target_id = target.id
		
		count = 0
		try:
			members = ctx.guild.fetch_members()
		except discord.HTTPException as e:
			logger.warn(f'Error on mary_all(): {e}')
			await ctx.respond('Error')
			return

		async for user in members:
			user_id = user.id

			if user.bot or user_id == target_id:
				continue

			if user_id not in self.married_users.get(target_id, []):
				if target_id not in self.married_users:
					self.married_users[target_id] = [user_id]
				else:
					self.married_users[target_id].append(user_id)

				if user_id not in self.married_users:
					self.married_users[user_id] = [target_id]
				else:
					self.married_users[user_id].append(target_id)

				if user_id in self.marry_requests[target_id]:
					self.marry_requests[target_id].remove(user_id)

				if target_id in self.marry_requests.get(user_id, []):
					# Shouldn't happen, but whatever
					self.marry_requests[user_id].remove(target_id)

				count += 1

		total = len(self.married_users[target_id])

		await ctx.respond(f'{target.display_name} has been married with {count} new peoples. (Total {total})')

	async def adopt(self, 
		ctx,
		user : Option(
			discord.Member,
			"Your futur child",
			name="user",
			required=True),
		answer : Option(
			str,
			"Accept or decline the adoption request",
			name="answer",
			default=None) = None
		):
		"Adopt somebody!"

		author = ctx.author
		author_id = author.id
		user_id = user.id

		self.adopt_requests = {int(k):v for k,v in self.adopt_requests.items()} # Json can't convert keys back to int ?
		self.adopted_users = {int(k):v for k,v in self.adopted_users.items()}


		if answer is None:
			if user_id == self.adopted_users.get(author_id, None):
				await ctx.respond(f'You have already adopted {user.display_name}!')
				return

			if user_id == author_id:
				await ctx.respond("You can't adopt yourself...")
				return

			if user.bot:
				await ctx.respond("You can't adopt a bot!")
				return

			if author.bot:
				await ctx.respond("A bot can't adopt somebody!")
				return


			if user_id not in self.adopt_requests:
				self.adopt_requests[user_id] = []

			if author_id in self.adopt_requests[user_id]: # Has already received a request
					desc = f'{user.mention}: {author.mention} has sent (another) adoption request.'

			else: # Hasn't received a request from author
				self.adopt_requests[user_id].append(author_id)
				desc = f'{user.mention}: {author.mention} would like to adopt you!'

			emb = {
				"title": "Adoption Request",
				"description": desc,
				"color": 0xea9ab,
				"footer": {
					"text": f"Use '.adopt @{author.display_name} accept' to accept!"
				}
			}

			await ctx.respond(embed=discord.Embed.from_dict(emb))

		else:
			# author: child / user: parent
			child, parent = author, user
			child_id, parent_id = author_id, user_id
			if answer in ('ok', 'accept', 'valid', 'yes', 'y', '1', 'oui', 'k', 'kay'):
				answer = True
			elif answer in ('no', 'nope', 'n', 'deny', 'refuse', 'non'):
				answer = False
			else:
				await ctx.respond(f'{answer} is an invalid answer!')
				return

			if parent_id not in self.adopt_requests.get(child_id, []):
				await ctx.respond(f'You have not received any adoption request by {parent.display_name}')

			if answer:
				self.adopted_users[child_id] = parent_id

				if parent_id in self.adopt_requests.get(child_id, []):
					self.adopt_requests[child_id].remove(parent_id)

				await ctx.respond(f'Congratulations! {child.mention} have been adopted by {parent.mention}!')
			else:
				await ctx.respond(f'{parent.mention}: Your request to adopt {child.mention} has been denied.')

		self.save_settings()

	async def adopted(self, 
		ctx
		):
		"List all adopted members"

		guild = ctx.guild

		emb = {
			"title": f"Relations on the {guild.name} server:",
			"color": 0xea9ab,
			"fields": [],
			"footer": {
				"text": "Use .marry @user to marry someone!"
			}
		}

		fields = []

		data = {}
		for child, parent in self.adopted_users.items():
			child = int(child) # Weird json thing
			if parent not in data:
				data[parent] = [child]
			else:
				data[parent].append(child)

		data = sorted(data.items(), key=lambda e: len(e[1]), reverse=True)

		for i, tmp in enumerate(data):
			parent_id, childs = tmp
			parent = guild.get_member(parent_id)

			if parent is not None:
				txt = ''
				for child_id in childs:
					child = guild.get_member(child_id)
					if child is not None:
						txt += f"- {child.display_name}\n"

				field = {
					"name": f'{i+1}: {parent.display_name} has adopted:',
					"value": txt,
					"inline": False
				}

				if txt != '': # At least one child in the guild
					fields.append(field)

		if len(fields) > 0:
			emb['fields'] = fields
			await ctx.respond(embed=discord.Embed.from_dict(emb))
		else:
			await ctx.respond('Nobody has been adopted yet!')

	async def emancipate(self, 
		ctx,
		user : Option(
			discord.Member,
			"The child you want to emancipate",
			name="dumped",
			required=True),
		):
		"Wanna get rid of your children?"

		parent = ctx.author
		parent_id = parent.id
		child = user
		child_id = user.id

		self.adopted_users = {int(k):v for k,v in self.adopted_users.items()}

		if parent_id == child_id:
			await ctx.respond(f"You can't get rid of yourself!")

		if parent_id == self.adopted_users[child_id]:
			del self.adopted_users[child_id]

			await ctx.respond(f'{parent.mention} got rid of {user.mention}!')

		else:
			await ctx.respond(f"You're not a parent of {user.display_name}!")

module_class = Relations