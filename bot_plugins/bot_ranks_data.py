#Discord_bot.py ranks data module



import base64
from io import BytesIO
import json
import os
import re
from PIL import Image

if 'GUILDS_ROLE_DATA' not in globals():
	globals()['GUILDS_ROLE_DATA'] = {}

class Role_Data:
	@classmethod
	def get_icon(cls, item, return_type='bytes'):
		rgx = r'\n.ITEM_NAME{background-position:(-?\d+)(?:px)? (-?\d+)(?:px)?;}'
		rgx = rgx.replace('ITEM_NAME', item)
		with open('./bot_plugins/ranks/icons-minecraft-0.4.css') as f:
			css_icons = f.read()
		match = re.search(rgx, css_icons)
		if match:
			coords = list(map(lambda e: -int(e), match.groups()))
			coords += [c + 32 for c in coords]

			img = Image.open("./bot_plugins/ranks/icons-minecraft-0.4.png")
			img = img.crop(coords)

			buffered = BytesIO()
			img.save(buffered, format="PNG")
			if return_type == 'bytes':
				img_bytes = buffered.getvalue()
				return img_bytes
			elif return_type == "base64":
				img_str = base64.b64encode(buffered.getvalue())
				return img_str
			elif return_type == "pil":
				return img

	def __init__(self, guild):
		guild_id = guild.id
		if guild_id in globals()['GUILDS_ROLE_DATA']:
			self.__dict__ = globals()['GUILDS_ROLE_DATA'][guild_id].__dict__
			return

		self.guild = guild
		self.guild_id = guild_id

		self.get_rank_data()

		globals()['GUILDS_ROLE_DATA'][guild_id] = self

	def get_rank_data(self):
		path = f'./bot_plugins/ranks/guilds/{self.guild_id}.json'
		if os.path.exists(path):
			with open(path, 'r') as f:
				self.guild_rank_data = json.load(f)
		else:
			with open('./bot_plugins/ranks/rank_data.json', 'r') as f:
				self.guild_rank_data = json.load(f)
			self.save_rank_data()

		self.guild_rank_data = sorted(self.guild_rank_data, reverse=True, key=lambda e: e['rank'])

		self.ranks = {role['rank']: role['lvl'] for role in self.guild_rank_data}
	
		self.find_ranks_ids()
		self.find_ranks_perms()

	def save_rank_data(self):
		path = f'./bot_plugins/ranks/guilds/{self.guild_id}.json'
		with open(path, 'w') as f:
			json.dump(self.guild_rank_data, f)

	def modify_rank(self, name, data):
		keys = ("lvl", "perms", "role_id", "color", "icon_css")
		data = {k:v for k,v in data.items() if k in keys}

		for i, rank in enumerate(self.guild_rank_data):
			if rank['name'] == name:
				rank = {k:data.get(k, v) for k,v in rank.items()}
				self.guild_rank_data[i] = rank
		
		self.save_rank_data()

	def find_ranks_ids(self):
		name_by_id = {role['name']: role['rank'] for role in self.guild_rank_data}
		self.ranks_ids = {}
		for role in self.guild.roles:
			if role.name in name_by_id:
				self.ranks_ids[name_by_id[role.name]] = role.id

	def find_ranks_perms(self):
		self.perms = {}
		current = set()
		for role in reversed(self.guild_rank_data):
			if role['perms'] is not None:
				current.update(role['perms'])
				self.perms[role['lvl']] = current

	def get_role_perms(self, rank):
		lvl = rank['lvl']
		perms = [k for i in range(lvl+1) for k in self.perms.get(i, [])]
		perms = set(perms)
		return perms



if __name__ == "__main__":
	with open('./bot_plugins/ranks/rank_data.json') as f:
		data = json.load(f)
	for rank in data:
		if rank['icon_css']:
			icon = Role_Data.get_icon(rank['icon_css'])
			print(rank['icon_css'], icon, '\n')