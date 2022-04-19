#Discord_bot.py reactions module

import discord
from discord import ApplicationContext, Option
import logging
logger = logging.getLogger('helium_logger')

# Reaction wrapper
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
			self.fill: ['fill'],
			self.unfill: ['unfill'],
			self.kiss: ['kiss'],
			self.welcome: ['welcome'],
			self.bang: ['bang'],
			self.hug: ['hug', 'hugs'],
			self.kick: ['kick'],
			self.punch: ['punch'],
			self.cry: ['cry', 'cries'],
			self.lick: ['lick', 'licks'],
			self.suck: ['suck', 'sucks'],
			self.cum: ['cum',' cums'],
			self.dodge: ['dodge'],
			self.heal: ['heal', 'heals'],
			self.fart: ['fart'],
			self.win: ['win', 'wins'],
			self.lost: ['lose', 'lost', 'loses'],
			self.pan: ['pan', 'throw_pan'],
			self.laugh: ['laugh', 'laughs', 'lol']
		}
		return txt_cmds

	@reaction({
		'self_action': '{target} is filling up!',
		'action': '{author} is filling {target}'
		})
	async def fill(self, 
		ctx : ApplicationContext,
		up : Option(
			str,
			"'up' keyword",
			name="up",
			choices=['up'],
			required=True),
		target : Option(
			discord.Member,
			"The target to fill up.",
			name='target',
			required=True)
		):
		"Fill up someone (bruh)"

		print('BYPASSED??')

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} is filling up*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} is filling {target.display_name}*')

	async def unfill(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The target to fill up.",
			name='target',
			required=True)
		):
		"Fill up someone (bruh)"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} is getting unfilled*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} is unfilling {target.display_name}*')

	async def kiss(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The target to kiss.",
			name='target',
			required=True)
		):
		"Kiss someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} kisses himself?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} kisses {target.display_name}*')

	async def welcome(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The user to welcome.",
			name='user',
			required=True)
		):
		"Welcome someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} welcomes himself?*')
		else:
			await ctx.respond(f'{ctx.author.display_name}: Welcome, {target.display_name} to T1T4N1UM Project!')

	async def bang(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person to bang.",
			name='target',
			required=True)
		):
		"Bangs someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} bangs himself?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} bangs {target.display_name}*')

	async def hug(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person to hug.",
			name='target',
			required=True)
		):
		"Hugs someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} is hugging himself, and starts crying...*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} hugs {target.display_name}*')

	async def kick(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person to kick.",
			name='target',
			required=True)
		):
		"Kicks someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} kicks himself?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} kicks {target.display_name}*')

	async def punch(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person to punch.",
			name='target',
			required=True)
		):
		"Punchs someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} punches himself?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} punch {target.display_name} in the face!*')

	async def cry(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person who made you cry.",
			name='target',
			default=None)=None
		):
		"Cries"

		if target is None:
			await ctx.respond(f'*{ctx.author.display_name} cries*')
		else:
			if target.id == ctx.author.id:
				await ctx.respond(f'*{ctx.author.display_name} cries on himself?*')
			else:
				await ctx.respond(f'*{ctx.author.display_name} is crying because of {target.display_name}!*')

	async def lick(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to lick.",
			name='target',
			default=None)=None
		):
		"Licks someone"

		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} licks himself?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} licks {target.display_name}!*')

	async def suck(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to suck.",
			name='target',
			default=None)=None
		):
		"Sucks someone"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} sucks*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} sucks {target.display_name}!*')

	async def cum(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to cum on.",
			name='target',
			default=None)=None
		):
		"Cum (in someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} is cumming*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} cums in {target.display_name}!*')

	async def dodge(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to dodge.",
			name='target',
			default=None)=None
		):
		"Dodge"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} dodges*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} dodges {target.display_name}!*')

	async def heal(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to heal.",
			name='target',
			default=None)=None
		):
		"Cum (in someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} heals*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} heals {target.display_name}!*')

	async def fart(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to cum on.",
			name='target',
			default=None)=None
		):
		"Fart (on someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} farted!*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} farts on {target.display_name}!*')

	async def win(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you have beaten.",
			name='target',
			default=None)=None
		):
		"Win (against someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} wins*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} won against {target.display_name}!*')

	async def lost(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you lost to.",
			name='target',
			default=None)=None
		):
		"Lose (against someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} lost*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} lost against {target.display_name}!*')

	async def pan(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you want to throw the pan to.",
			name='target',
			default=None)=None
		):
		"Throw a pan (at someone)"

		if target is None:
			await ctx.respond(f'*{ctx.author.display_name} threw a pan')
		if target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} hits himself with a pan?*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} threw a pan at {target.display_name}!*')

	async def laugh(self, 
		ctx : ApplicationContext,
		target : Option(
			discord.Member,
			"The person you laugh at.",
			name='target',
			default=None)=None
		):
		"Laugh (at someone)"

		if target is None or target.id == ctx.author.id:
			await ctx.respond(f'*{ctx.author.display_name} is laughing*')
		else:
			await ctx.respond(f'*{ctx.author.display_name} is laughing at {target.display_name}!*')



module_class = Simple_Reactions
