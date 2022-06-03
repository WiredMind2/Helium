#Discord_bot.py ranks data module



import base64
from io import BytesIO
import json
import os
import re
from PIL import Image


class Role_Data:
	perms = {
		0: [ # Dirt
			'connect',
			'external_emojis',
			'read_messages',
			'send_messages',
			'speak',
			'send_messages_in_threads',
			'use_voice_activation',
			'view_channel'
		],
		3: [ # Coal
			'add_reactions',
			'create_instant_invite',
			'embed_links',
			'read_message_history',
			'stream',
			'use_slash_commands'
		],
		5: [ # Copper
			'attach_files',
			'external_stickers',
			'request_to_speak'
		],
		10: [ # Iron
			'change_nickname',
			'send_tts_messages'
		],
		15: [ # Lapis
			'create_private_threads',
			'create_public_threads',
			'manage_nicknames'
		],
		20: [ # Redstone
			'manage_messages',
			'manage_emojis',
			# 'moderate_members',
			'mute_members'
		],
		23: [ # Gold
			'deafen_members',
			'move_members'
		],
		25: [ # Amethyst
			'manage_threads',
			'priority_speaker'
		],
		30: [ # Diamond
			'manage_events',
			'start_embedded_activities'
		],
		35: [ # Netherite
			'manage_roles',
			'manage_webhooks',
			'view_audit_log'
		],
	}

	ranks = {
        30: 125, # command block
        29: 120, # warden
        28: 115, # wither
        27: 110, # ender dragon
        26: 105, # shulker
        25: 100, # enderman
        24: 95, # wither skeleton
        23: 90, # ghast
        22: 85, # blaze
        21: 80, # magma cube
        20: 75, # piglin
        19: 70, # guardian
        18: 65, # phantom
        17: 60, # creeper
        16: 55, # skeleton
        15: 50, # zombie
        14: 45, # ender egg
        13: 40, # beacon
        12: 35, # nether star
        11: 30, # emerald
        10: 25, # netherite
        9: 20, # diamond
        8: 18, # amethyst
        7: 15, # gold
        6: 13, # redstone
        5: 10, # lapis
        4: 8, # iron
        3: 5, # copper
        2: 3, # coal
        1: 0 # dirt
    }

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


if __name__ == "__main__":
	with open('./bot_plugins/ranks/rank_data.json') as f:
		data = json.load(f)
	for rank in data:
		if rank['icon_css']:
			icon = Role_Data.get_icon(rank['icon_css'])
			print(rank['icon_css'], icon, '\n')