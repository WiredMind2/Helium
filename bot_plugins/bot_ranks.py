#Discord_bot.py ranks module

import asyncio
import io
import json
import logging
from math import sqrt

import discord
import requests
from discord import Option
from PIL import Image, ImageDraw, ImageFont, ImageOps

try:
	from .bot_ranks_data import Role_Data
except ImportError:
	from bot_ranks_data import Role_Data


logger = logging.getLogger('helium_logger')

class Role_Management():
	"""Role management: role"""
	def initialize(self):
		txt_cmds = {
			self.update_roles: ['update_roles', 'get_roles', 'role', 'rank'],
			self.generate_roles: ['generate_roles'],
			self.register_roles: ['register_role'],
			self.roles: ['roles', 'ranks'],
		}

		self.ranks_ids = {
			29: 977260499320324176, # warden
			28: 977260329027375214, # wither
			27: 977260419502731295, # ender dragon
			26: 977260008305737809, # shulker
			25: 977259295278264370, # enderman
			24: 977259286352756746, # wither skeleton
			23: 977259281009246298, # ghast
			22: 977259276596805632, # blaze
			21: 977259290794537050, # magma cube
			20: 977259272033407037, # piglin
			19: 977259267482599494, # guardian
			18: 977259179137957951, # phantom
			17: 977259004193562656, # creeper AWH MEN
			16: 977258836865990716, # skeleton
			15: 977258724160856136, # zombie
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
		# perms : Option(
		# 	bool,
		# 	"Also show the perms",
		# 	name="show_perms",
		# 	default=False)=False,
		):
		"List all available ranks"

		import json
		
		with open('./bot_plugins/ranks/rank_data.json') as f:
			ranks = json.load(f)

		ranks = sorted(ranks, key=lambda e: e['lvl'], reverse=True)

		await ctx.defer()

		imgs = []
		for rank in ranks:
			img = self.generate_role_img_row(rank)
			# file = discord.File(img, filename=f"{rank['name']}.png")

			imgs.append(img)

		if imgs == []:
			embed = discord.Embed(
				title = 'No roles found!',
				description = 'No roles have been registered yet!',
				color = 0x0000FF
			)
			embed.set_footer(
				text = 'Use .register_role to register a new role'
			)
			embed = discord.Embed.from_dict(embed)
			await ctx.respond(embed=embed)
		else:
			title_embed = discord.Embed(
				title = f'Roles on {ctx.guild.name}',
				description = f'{len(imgs)} roles have been registered:',
				colour = 0x0000FF
			)
			
			columns = 2
			width, height = imgs[0].size
			off = (10, 10)
			width += off[0]
			height += off[1]
			max_width, max_height = width * columns + off[0], (len(imgs) // columns) * height + off[1]

			merged = Image.new('RGBA', (max_width, max_height))
			imgs = iter(imgs)
			row = 0
			while True:
				for col in range(columns):
					img = next(imgs, None)
					if img is None:
						break
					pos = (col * width + off[0], row * height + off[1])
					merged.paste(img, pos)
				if img is None:
					break
				row += 1
			merged.show()
			
			b = io.BytesIO()
			merged.save(b, "PNG")
			b.seek(0)

			file = discord.File(b, filename='ranks.png')
			await ctx.respond(embed=title_embed)
			await ctx.send(file=file)
		return 

	@classmethod
	def generate_role_img_row(self, rank):
		size = (800, 200)
		fontname = "comicbd.ttf"
		img = Image.new('RGBA', size, color=0)
		d = ImageDraw.Draw(img)

		bg = (50, 50, 50)
		fg = (200, 200, 255)

		# Partial border
		coords_size = (800, 200)
		coords = tuple(int(self.factor_from_bb((100, 0), coords_size)[i] * size[i]) for i in range(2))
		border = 10
		d.rectangle((*coords, *size), fill=0, outline=bg, width=border)

		# Title
		coords = ((220, 50), (780, 100))
		coords_size = (800, 200)

		self.add_text(d, coords, coords_size, rank['name'], fontname, fg, size)

		# Level
		coords = ((230, 110), (600, 140))
		coords_size = (800, 200)

		txt = f'Level {str(rank["lvl"])}'
		
		self.add_text(d, coords, coords_size, txt, fontname, fg, size)

		# Circle
		center, rayon = (100, 100), 100
		coords_size = (800, 200)

		coords = (
			(center[0] - rayon, center[1] - rayon),
			(center[0] + rayon, center[1] + rayon)
		)

		pos = [tuple([
				self.factor_from_bb(coord, coords_size)[i] * size[i]
				for i in range(2)])
			for coord in coords
		]

		d.ellipse(pos, bg)

		# Icon
		icon = Role_Data.get_icon(rank['icon_css'], return_type='pil')

		offset = 50 # Distance between the circle border and the icon
		fac = max(coords_size[0] / size[0], coords_size[1] / size[1])
		rayon_fac = (rayon + offset) * fac
		circle_border = rayon_fac * (1 - sqrt(2) / 2)
		
		coords = (
			(coords[0][0] + circle_border, coords[0][1] + circle_border),
			(coords[1][0] - circle_border, coords[1][1] - circle_border))
		icon_size = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])

		coords = list(map(lambda e: tuple(map(int, e)), coords))
		icon_size = list(map(int, icon_size))

		if icon.size != icon_size:
			icon = icon.resize(icon_size)

		img.paste(icon, coords[0], icon)

		return img

	@classmethod
	def generate_role_banner(self, rank):
		# Not used
		size = (800, 300)
		fontname = "comicbd.ttf"
		img = Image.new('RGBA', size, color=0)
		d = ImageDraw.Draw(img)

		# Border
		border = 10
		d.rectangle((0, 0, *size), fill=0, outline=(0,0,0), width=border)

		# Title
		coords = ((350, 40), (750, 100))
		coords_size = (800, 300)
		col = (255, 255, 255)

		self.add_text(d, coords, coords_size, rank['name'], fontname, col, size)

		# Level
		coords = ((350, 125), (500, 150))
		coords_size = (800, 300)
		col = (255, 255, 255)
		txt = f'Level {str(rank["lvl"])}'
		
		self.add_text(d, coords, coords_size, txt, fontname, col, size)

		# Circle
		center, rayon = (150, 150), 100
		coords = (
			(center[0] - rayon, center[1] - rayon),
			(center[0] + rayon, center[1] + rayon)
		)
		coords_size = (800, 300)
		col = (255, 255, 255)

		pos = [tuple([
				self.factor_from_bb(coord, coords_size)[i] * size[i]
				for i in range(2)])
			for coord in coords
		]

		d.ellipse(pos, col)

		# Icon
		icon = Role_Data.get_icon(rank['icon_css'], return_type='pil')
		
		rayon_fac = rayon * max(coords_size[0] / size[0], coords_size[1] / size[1])
		circle_border = rayon_fac * (1 - sqrt(2) / 2) # (2 * sqrt(3)) / 2
		
		coords = (
			(coords[0][0] + circle_border, coords[0][1] + circle_border),
			(coords[1][0] - circle_border, coords[1][1] - circle_border))
		icon_size = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])

		coords = list(map(lambda e: tuple(map(int, e)), coords))
		icon_size = list(map(int, icon_size))

		if icon.size != icon_size:
			icon = icon.resize(icon_size)

		img.paste(icon, coords[0])

		img.show()

	@classmethod
	def get_fontsize(self, fontname, txt, size, factor):
		max_x, max_y = (size[0] * factor[0], size[1] * factor[1])
		fontsize = 1
		font = ImageFont.truetype(fontname, fontsize)
		txt_size = font.getsize(txt)
		while txt_size[0] < max_x and txt_size[1] < max_y:
			fontsize += 1
			font = ImageFont.truetype(fontname, fontsize)
			txt_size = font.getsize(txt)
		
		font = ImageFont.truetype(fontname, fontsize-1) # Don't get out of bounds
		a = font.getsize(txt)
		return font
	
	@classmethod
	def factor_from_bb(self, bb, size):
		if len(bb) == 4:
			bb = (bb[2]-bb[0], bb[3]-bb[1])
		elif len(bb) == 2:
			if not isinstance(bb[0], int):
				bb = (bb[1][0]-bb[0][0], bb[1][1]-bb[0][1])
		fac = (
			(bb[0])/size[0], 
			(bb[1])/size[1]
		)
		return fac

	@classmethod
	def add_text(self, d, coords, coords_size, text, fontname, col=None, size=None):
		if size is None:
			size = d.im.size
		
		title_fac = self.factor_from_bb(coords, coords_size)
		pos_fac = self.factor_from_bb(coords[0], coords_size)
		pos = (pos_fac[0] * size[0], pos_fac[1] * size[1])

		font = self.get_fontsize(fontname, text, size, title_fac)
		d.text(pos, text, font=font, fill=(255,255,255))

	async def update_single_role(self, msg, member):
		"NOT a bot command! - Called by on_message()"

		url = f'https://mee6.xyz/api/plugins/levels/leaderboard/{msg.guild.id}'
		try:
			headers = {
				'Accept': 'application/json'
			}
			r = requests.get(url, headers=headers)

		except Exception as e:
			logger.info(f'Error on Role_Management.roles(): {e}')
			await msg.channel.send('Error while fetching mee6 levels!')
			return
		else:
			data = r.json()

		user_lvl = next(filter(lambda e: e['id'] == member.id, data), None)
			
		if user_lvl is None:
			logger.info(f'User {member.display_name}, id {member.id} not found in mee6 lvl data')
			return

		new_rank = None # The level of the new rank
		for rank, lvl in Role_Data.ranks.items():
			if lvl <= user_lvl['level']:
				new_rank = rank
				break
		
		if new_rank is None:
			# User lvl < 0??
			logger.warn('Negative level??')
			return

		new_rank_id = self.ranks_ids.get(new_rank, None) # Get the closest existing rank for the required lvl
		while new_rank_id is None:
			if new_rank == 0:
				break
			new_rank -= 1
			new_rank_id = self.ranks_ids.get(new_rank, None)
		
		if new_rank_id is None:
			# No rank <= lvl
			logger.warn('No rank found!')
			return

		to_remove = []
		add_role = True
		for role in member.roles:
			if role.id in self.ranks_ids.values():
				if role.id != new_rank_id:
					to_remove.append(role)
				else:
					add_role = False

		tasks = []
		if len(to_remove) > 0:
			t = member.remove_roles(*to_remove)
			tasks.append(t)

		if add_role:
			new_role = msg.guild.get_role(new_rank_id)
			if new_role is not None: # Does the role actually exists?
				t = member.add_roles(new_role)
				tasks.append(t)

		try:
			await asyncio.gather(*tasks)
		except discord.Forbidden:
			logger.warn(f'Forbidden for user: {member.display_name}')
		else:
			if add_role:
				logger.info(f'{new_role.name}: {member.display_name}, removed: {[r.name for r in to_remove]}')

				embed = {
					"type": "rich",
					"title": 'Roles update!',
					"description": 'Roles updated for:',
					"color": 0x0000FF,
					"fields": [{
						'name': f"{member.display_name}: {new_role.name}",
						'value': f"And {len(to_remove)} removed roles" if len(to_remove) > 0 else 'No roles removed'
					}]
				}

				embed = discord.Embed.from_dict(embed)
				await msg.guild.send(embed=embed)

	async def update_roles(self, ctx):
		"Update ranks for all members (use this to get a new rank!)"

		await ctx.defer()

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
			for rank, lvl in Role_Data.ranks.items():
				if lvl <= user_lvl['level']:
					new_rank = rank
					break
			
			if new_rank is None:
				# User lvl < 0??
				continue

			new_rank_id = self.ranks_ids.get(new_rank, None)
			while new_rank_id is None:
				if new_rank == 0:
					break
				new_rank -= 1
				new_rank_id = self.ranks_ids.get(new_rank, None)
			
			if new_rank_id is None:
				continue

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
		await ctx.respond(embed=embed)

	async def generate_roles(self, 
		ctx
		):
		"Generate roles from a list of rules (admin only!)"

		if not self.is_admin(ctx.author):
			ctx.respond(f'Only the bot\'s admin can use this command!')

		await ctx.respond('Updating ranks:')
		
		with open('./bot_plugins/ranks/rank_data.json') as f:
			data = json.load(f)

		use_icon = 'ROLE_ICONS' in ctx.guild.features

		for rank in data:
			kwargs = {k: True for k in self.get_role_perms(rank)}

			usr_perms = discord.Permissions.none()
			usr_perms.update(**kwargs)

			name = rank['name']
			# color = discord.Color.from_rgb(*rank['color'])
	
			role_id = rank['role_id']
			if role_id is None:
				await ctx.send(f'{name} role is unknown!')
				continue
			role = ctx.guild.get_role(role_id)

			kwargs = {
				'name':name, 
				'permissions':usr_perms, 
				# colour:color,
				'hoist':True,
				'mentionable':False
			}

			if use_icon:
				icon = Role_Data.get_icon(rank['icon_css'])
				kwargs['icon'] = icon

			try:
				await role.edit(**kwargs)
			except discord.Forbidden as e:
				logger.warn(f'Forbidden for role: {role.name} - {e}')
			except discord.HTTPException as e:
				logger.error(f'Error for role: {role.name}, {e}')
			else:
				log_perms = False
				if log_perms:
					perms_txt = ' - ' + ', '.join(kwargs.keys())
				else:
					perms_txt = ''
				txt = f'{role.name}: {len(kwargs)} perms{perms_txt}'
				logger.info(txt)
				await ctx.send(txt)

	@classmethod
	def get_role_perms(self, rank):
		# lvl = Role_Data.ranks[rank]
		lvl = rank['lvl']
		perms = [k for i in range(lvl+1) for k in Role_Data.perms.get(i, [])]
		return perms

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

if __name__ == "__main__":
	with open('./bot_plugins/ranks/rank_data.json') as f:
		data = json.load(f)
	rank = data[5]
	Role_Management.generate_role_img_row(rank)