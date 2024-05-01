#Discord_bot.py reactions module

import json
import logging
import os
from types import MethodType

import discord

logger = logging.getLogger('helium_logger')

# Reaction wrapper - TODO
def reaction(action_data):
	def decorator(func):
		async def wrapper(self, *args, **kwargs):
			if target is None:
				if 'no_target' in action_data:
					action = action_data['no_target']
				else:
					await ctx.respond('You need to specify a target!')
					return
			elif target.id == ctx.author.id:
				if 'self_action' in action_data:
					action = action_data['self_action']
				else:
					await ctx.respond("You can't do that to yourself!")
					return
			else:
				action = action_data['action']

			swaps = {
				'author':ctx.author.display_name, 
				'target':target.display_name
			}

			action = '*' + action.replace(**swaps) + '*'
		return wrapper
	return decorator

class Simple_Reactions:
	"""Reactions: react"""
	def initialize(self):
		txt_cmds = {}

		with open(os.path.join(os.path.dirname(__file__), 'reactions_data.json'), 'r') as f:
			reactions = json.load(f)

		for reaction in reactions:
			func = self.reaction_wrapper(reaction)
			txt_cmds[func] = reaction['commands']

		return txt_cmds
	
	@classmethod
	async def reaction(self, ctx, action_data, target=None):
		if target is None:
			if 'no_target' in action_data:
				action = action_data['no_target']
			else:
				await ctx.respond('You need to specify a target!')
				return
		elif target.id == ctx.author.id:
			if 'self_action' in action_data:
				action = action_data['self_action']
			else:
				await ctx.respond("You can't do that to yourself!")
				return
		else:
			if 'action' in action_data:
				action = action_data['action']
			else:
				await ctx.respond("You can't do that to someone else!")
				return

		swaps = {
			'{author}':ctx.author.display_name, 
			'{target}':target.display_name if target else ''
		}

		for k, v in swaps.items():
			action = action.replace(k, v)
		action = '*' + action + '*'
		await ctx.respond(action)

	def reaction_wrapper(self, action_data):
		func_temp = (
		"@discord.option(\n"
		"	name = 'target',\n"
		"	description = '{arg_desc}')\n"
		"async def {name}(self, ctx,\n"
		"	target : discord.Member = None\n"
		"	):\n"
		"	'{desc}'\n"
		"	await self.reaction(ctx, {action_data}, target)\n"
		)
		
		name = action_data['name']
		func_temp = func_temp.format(
			name = name,
			desc = action_data['desc'],
			arg_desc = action_data['arg_desc'],
			action_data=action_data
		)
		exec(func_temp)
		func = locals()[name]
		method = MethodType(func,self)
		setattr(self, name, method)
		func = getattr(self, name)
		return func


module_class = Simple_Reactions
