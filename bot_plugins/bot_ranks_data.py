#Discord_bot.py ranks data module



class Role_Data:
	perms = {
		1: [ # Dirt
			'connect',
			'external_emojis',
			'read_messages',
			'send_messages',
			'speak',
			'send_messages_in_threads',
			'use_voice_activation',
			'view_channel'
		],
		2: [ # Coal
			'add_reactions',
			'create_instant_invite',
			'embed_links',
			'read_message_history',
			'stream',
			'use_slash_commands'
		],
		3: [ # Copper
			'attach_files',
			'external_stickers',
			'request_to_speak'
		],
		4: [ # Iron
			'change_nickname',
			'send_tts_messages'
		],
		5: [ # Lapis
			'create_private_threads',
			'create_public_threads',
			'manage_nicknames'
		],
		6: [ # Redstone
			'manage_messages',
			# 'moderate_members',
			'mute_members'
		],
		7: [ # Gold
			'deafen_members',
			'move_members'
		],
		8: [ # Amethyst
			'manage_threads',
			'priority_speaker'
		],
		9: [ # Diamond
			'manage_emojis',
			'manage_events',
			'start_embedded_activities'
		],
		10: [ # Netherite
			'manage_roles',
			'manage_webhooks',
			'view_audit_log'
		],
		11: [ # Emerald
		],
		12: [ # Nether star
		],
		13: [ # Beacon
		],
		14: [ # Ender Egg
		],
	}

	ranks = {
		14: 50, # ender egg
		13: 45, # beacon
		12: 40, # nether star
		11: 35, # emerald
		10: 30, # netherite
		9: 25, # diamond
		8: 20, # amethyst
		7: 18, # gold
		6: 15, # redstone
		5: 13, # lapis
		4: 10, # iron
		3: 7, # copper
		2: 5, # coal
		1: 0 # dirt
	}