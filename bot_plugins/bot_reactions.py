#Discord_bot.py reactions module

from types import MethodType
import discord
from discord import Option
import logging
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
		txt_cmds = {
		}

		reactions = [
			{
				'name': 'unfill',
				'desc': 'Unfill someone',
				'arg_desc': 'The target to unfill.',
				'no_target': '{author} is getting unfilled',
				'self_action': '{author} is getting unfilled',
				'action': '{author} is unfilling {target}',
				'commands': ['unfill']
			},{
				'name': 'fill',
				'desc': 'Fill up someone (bruh)',
				'arg_desc': 'The target to fill up.',
				'no_target': None,
				'self_action': '{author} is filling up',
				'action': '{author} is filling {target}',
				'commands': ['fill']
			},{
				'name': 'kiss',
				'desc': 'Kiss someone',
				'arg_desc': 'The target to kiss.',
				'no_target': None,
				'self_action': '{author} kisses himself??',
				'action': '{author} kisses {target}',
				'commands': ['kiss']
			},{
				'name': 'welcome',
				'desc': 'Welcome someone',
				'arg_desc': 'The user to welcome.',
				'no_target': None,
				'self_action': '{author} welcomes himself',
				'action': '{author}: Welcome, {target} to T1T4N1UM Project!',
				'commands': ['welcome']
			},{
				'name': 'bang',
				'desc': 'Bangs someone',
				'arg_desc': 'The person to bang.',
				'no_target': 'BANG!',
				'self_action': '{author} bangs himself?',
				'action': '{author} bangs {target}',
				'commands': ['bang', 'bangs']
			},{
				'name': 'hug',
				'desc': 'Hugs someone',
				'arg_desc': 'The person to hug.',
				'no_target': '{author} is hugging himself, and starts crying...',
				'self_action': '{author} is hugging himself, and starts crying...',
				'action': '{author} hugs {target}',
				'commands': ['hug', 'hugs']
			},{
				'name': 'kick',
				'desc': 'Kicks someone',
				'arg_desc': 'The person to kick.',
				'no_target': None,
				'self_action': '{author} kicks himself?',
				'action': '{author} kicks {target}',
				'commands': ['kick', 'kicks']
			},{
				'name': 'punch',
				'desc': 'Punchs someone',
				'arg_desc': 'The person to punch.',
				'no_target': None,
				'self_action': '{author} punches himself?',
				'action': '{author} punches {target}',
				'commands': ['punch', 'punches', 'punchs']
			},{
				'name': 'cry',
				'desc': 'Cries',
				'arg_desc': 'The person who made you cry.',
				'no_target': '{author} cries',
				'self_action': '{author} cries on himself?',
				'action': '{author} is crying because of {target}',
				'commands': ['cry', 'cries']
			},{
				'name': 'lick',
				'desc': 'Licks someone',
				'arg_desc': 'The person you want to lick.',
				'no_target': None,
				'self_action': '{author} licks himself?',
				'action': '{author} licks {target}',
				'commands': ['lick', 'licks']
			},{
				'name': 'suck',
				'desc': 'Sucks someone',
				'arg_desc': 'The person you want to suck.',
				'no_target': '{author} sucks',
				'self_action': '{author} sucks himself',
				'action': '{author} sucks {target}',
				'commands': ['suck', 'sucks']
			},{
				'name': 'cum',
				'desc': 'Cum (in someone)',
				'arg_desc': 'The person you want to cum on.',
				'no_target': '{author} is cumming',
				'self_action': '{author} is cumming',
				'action': '{author} cums in {target}',
				'commands': ['cum', 'cums']
			},{
				'name': 'dodge',
				'desc': 'Dodge',
				'arg_desc': 'The person you want to dodge',
				'no_target': '{author} dodges',
				'self_action': '{author} dodges',
				'action': '{author} dodges {target}',
				'commands': ['dodge', 'dodges']
			},{
				'name': 'heal',
				'desc': 'Heals (someone)',
				'arg_desc': 'The person you want to heal.',
				'no_target': '{author} is healing',
				'self_action': '{author} heals himself',
				'action': '{author} heals {target}',
				'commands': ['heal', 'heals']
			},{
				'name': 'fart',
				'desc': 'Fart (on someone)',
				'arg_desc': 'The person you want to fart on.',
				'no_target': '{author} farted!',
				'self_action': '{author} farts on himself',
				'action': '{author} farts on {target}',
				'commands': ['fart', 'farts']
			},{
				'name': 'win',
				'desc': 'Win (against someone)',
				'arg_desc': 'The person you have beaten',
				'no_target': '{author} wins',
				'self_action': '{author} is the winner!',
				'action': '{author} won against {target}',
				'commands': ['win', 'wins']
			},{
				'name': 'lose',
				'desc': 'Lose (against someone)',
				'arg_desc': 'The person you lost to',
				'no_target': '{author} loses',
				'self_action': '{author} lost',
				'action': '{author} lost against {target}',
				'commands': ['lose', 'lost']
			},{
				'name': 'pan',
				'desc': 'Throw a pan (at someone)',
				'arg_desc': 'The person you want to throw the pan to.',
				'no_target': '{author} threw a pan.',
				'self_action': '{author} hits himself with a pan?',
				'action': '{author} threw a pan at {target}',
				'commands': ['pan']
			},{
				'name': 'laugh',
				'desc': 'Laugh (at someone)',
				'arg_desc': 'The person you laugh at',
				'no_target': '{author} laugh',
				'self_action': '{author} is laughing at himself',
				'action': '{author} is laughing at {target}',
				'commands': ['laugh', 'lol']
			},{
				'name': 'leave',
				'desc': 'Leaves (someone)',
				'arg_desc': 'The person you want to leave',
				'no_target': '{author} leaves',
				'self_action': '{author} left the chat!',
				'action': '{author} left {target}',
				'commands': ['leave', 'left']
			},
		]

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
