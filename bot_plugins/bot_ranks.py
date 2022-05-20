#Discord_bot.py ranks module

import requests
import asyncio
import logging
logger = logging.getLogger('helium_logger')

from .bot_ranks_data import Role_Data
import discord
from discord import Option

class Role_Management(Role_Data):
	"""Role management: role"""
	def initialize(self):
		txt_cmds = {
			self.update_roles: ['update_roles', 'get_roles', 'role', 'rank'],
			self.generate_roles: ['generate_roles'],
			self.register_roles: ['register_role'],
			self.roles: ['roles', 'ranks'],
		}

		self.ranks_ids = {
			14: 974231330705534996, # ender egg
			13: 974231044209385502, # beacon
			12: 976014698971529228, # nether star
			11: 839779416326537237, # emerald
			10: 878564206025248788, # netherite
			9: 839779276924649472, # diamond
			8: 974004158355079228, # amethyst
			7: 839771240066580500, # gold
			6: 839771165144121364, # redstone
			5: 839771065366347777, # lapis
			4: 839771007656001546, # iron
			3: 917778148798648321, # copper
			2: 839770919039402004, # coal
			1: 917774707049254982 # dirt
		}

		return txt_cmds

	async def roles(self,
		ctx,
		perms : Option(
			bool,
			"Also show the perms",
			name="show_perms",
			default=False)=False,
		):
		"List all available ranks"
		
		roles = []
		role_ids = {v: k for k, v in self.ranks_ids.items()}
		for role in ctx.guild.roles:
			if role.id in role_ids:
				roles.append((role_ids[role.id], role))
		
		roles = sorted(roles, key=lambda e: e[0], reverse=True)

		fields = []
		# TODO - Embed
		for lvl, role in roles:
			data = {
				'name': '​' + f'{role.name}'.center(20, ' ') + '​',
				'value': '​' + f'Level {lvl}'.center(20, ' ') + '​',
				'inline': True
			}
			print(data)
			fields.append(data)

		if fields == []:
			embed = {
				"type": "rich",
				"title": 'No roles found!',
				"description": 'No roles have been registered yet!',
				"color": 0x0000FF,
				"footer": {
					'text': 'Use .register_role to register a new role'
				}
			}
		else:
			embed = {
				"type": "rich",
				"title": f'Roles on {ctx.guild.name}',
				"description": f'{len(fields)} roles have been registered:',
				"color": 0x0000FF,
				"fields": fields
			}
			
		embed = discord.Embed.from_dict(embed)
		await ctx.respond(embed=embed)

	async def update_roles(self, ctx):
		"Update ranks for all members (use this to get a new rank!)"

		try:
			members = ctx.guild.fetch_members()
		except discord.HTTPException as e:
			logger.info(f'Error on update_roles(): {e}')
			await ctx.respond('Error')
			return

		url = f'https://mee6.xyz/api/plugins/levels/leaderboard/{ctx.guild.id}'
		try:
			headers = {
				'Accept': 'application/json'
			}
			r = requests.get(url, headers=headers)

		except Exception as e:
			logger.info(f'Error on Role_Management.roles(): {e}')
			await ctx.respond('Error while fetching mee6 levels!')
			return
		else:
			data = r.json()
		level_data = {m['id']: m for m in data['players']}

		added = {}

		async for user in members:
			if user.bot:
				continue

			user_lvl = level_data.get(str(user.id), None)
			
			if user_lvl is None:
				# logger.info(f'User {user.display_name}, id {user.id} not found in mee6 lvl data')
				continue

			new_rank = None
			for rank, lvl in self.ranks.items():
				if lvl <= user_lvl['level']:
					new_rank = rank
					break
			
			if new_rank is None:
				# User lvl < 0??
				continue

			new_rank_id = self.ranks_ids[new_rank]

			to_remove = []
			add_role = True
			for role in user.roles:
				if role.id in self.ranks_ids.values():
					if role.id != new_rank_id:
						to_remove.append(role)
					else:
						add_role = False

			tasks = []
			if len(to_remove) > 0:
				t = user.remove_roles(*to_remove)
				tasks.append(t)

			if add_role:
				new_role = ctx.guild.get_role(new_rank_id)
				if new_role is not None: # Does the role actually exists?
					t = user.add_roles(new_role)
					tasks.append(t)
			
			try:
				await asyncio.gather(*tasks)
			except discord.Forbidden:
				logger.warn(f'Forbidden for user: {user.display_name}')
			else:
				if add_role:
					logger.info(f'{new_role.name}: {user.display_name}, removed: {[r.name for r in to_remove]}')
					added[user] = {'new_role': new_role, 'to_remove': to_remove}
				else:
					pass
					# logger.info(f'OK: {user.display_name}, removed: {[r.name for r in to_remove]}')

		if len(added) > 0:
			fields = [
				{
					'name': f"{user.display_name}: {data['new_role'].name}",
					'value': f"And {len(data['to_remove'])} removed roles" if len(data['to_remove']) > 0 else 'No roles removed'
				} for user, data in added.items()
			]

			embed = {
				"type": "rich",
				"title": 'Roles update!',
				"description": 'Roles updated for:',
				"color": 0x0000FF,
				"fields": fields
			}

		else:
			embed = {
				"type": "rich",
				"title": 'No new roles to update!',
				"description": 'Current roles have been conserved for all members.',
				"color": 0x0000FF,
			}

		embed = discord.Embed.from_dict(embed)
		out = await ctx.respond(embed=embed)

	async def generate_roles(self, 
		ctx
		):
		"Generate roles from a list of rules (admin only!)"

		if not self.is_admin(ctx.author):
			ctx.respond(f'Only the bot\'s admin can use this command!')

		for rank in range(1, len(self.ranks_ids)+1):
			kwargs = {k: True for i in range(1, rank+1) for k in self.perms[i]}

			usr_perms = discord.Permissions.none()
			usr_perms.update(**kwargs)
			
			role_id = self.ranks_ids[rank]
			role = ctx.guild.get_role(role_id)


			try:
				await role.edit(permissions=usr_perms)
			except discord.Forbidden:
				logger.warn(f'Forbidden for role: {role.name}')
			except discord.HTTPException as e:
				logger.error(f'Error for role: {role.name}, {e}')
			else:
				log_perms = False
				if log_perms:
					perms_txt = ' - ' + ', '.join(kwargs.keys())
				else:
					perms_txt = ''
				logger.info(f'{role.name}: {len(kwargs)} perms{perms_txt}')

	async def register_roles(self, 
		ctx,
		role : Option(
			discord.Role,
			"The role to register",
			name="role",
			),
		lvl : Option(
			int,
			"The role level",
			name="level",
			),
		):
		"Register a new role (admin only!)"

		if not self.is_admin(ctx.author):
			ctx.respond(f'Only the bot\'s admin can use this command!')
			return
		
		role_id = role.id
		if lvl not in self.ranks_ids:
			self.ranks_ids[lvl] = role_id
			await ctx.respond(f'Role {role.display_name} is now level {lvl}!')
		else:
			text = f'Inserted {role.display_name} with level {lvl}!'
			while lvl in self.ranks_ids:
				next_role_id = self.ranks_ids[lvl]
				self.ranks_ids[lvl] = role_id
				role_id = next_role_id
				lvl += 1
			await ctx.respond(text)

module_class = Role_Management
