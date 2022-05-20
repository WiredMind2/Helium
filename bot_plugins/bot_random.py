#Discord_bot.py random module

import discord
from discord import Option

import random
import re
import time
import logging
logger = logging.getLogger('helium_logger')

class Random:
	"""Random: rand"""
	def initialize(self):
		txt_cmds = {
			self.fight: ['battle', 'clash', 'fight', 'versus'],
			self.choose: ['choose', 'which'],
			self.dice: ['dice', 'random'],
			self.kill: ['kill'],
			self.suicide: ['suicide', 'die']
		}

		return txt_cmds

	async def dice(self, 
		ctx,
		hi : Option(
			int,
			"Max value", 
			name="max", 
			default=6), 
		lo : Option(
			int,
			"Min value", 
			name="min", 
			default=0)
		):
		"A random number:\n > .random\n > .random 50 100"
		if lo > hi:
			hi, lo = lo, hi
		num = random.randrange(lo+1, hi+1)

		entities = ['eggs', 'cars', 'children', 'cats', 'dogs', 'carrots']

		await ctx.respond(f'{num} {random.choice(entities)}')

	async def choose(self, 
		ctx,
		choices : Option(
			str,
			"List of things to choose from",
			name="choices")
		):
		"If you have troubles making a decision:\n > .choose pasta pizza"
		# TODO
		args += choices.split()
		if len(args) == 0:
			await ctx.respond('I choose nothing?')
			return
		elif len(args) == 1:
			await ctx.respond('Do I even have a choice??')
			return
		await ctx.respond(f'I choose {random.choice(args)}!')

	async def fight(self, 
		ctx,
		args : Option(
			str,
			"List of fighters",
			name="fighters"),
		):
		"Starts a pokemon-like fight:\n > .fight pikachu putin"
		
		args = args.split()
		if len(args) == 0:
			await ctx.respond("You can't fight yourself??")
			return
		elif len(args) == 1:
			if ctx.author.mention == args[0]:
				await ctx.respond("You can't fight yourself??")
				return
			args.append(ctx.author.mention)

		rgx = re.compile(r'<@[&!]?(\d{17,19})>')

		fighters = {}
		for f in args:
			m = re.match(rgx, f)
			if m:
				u_id = int(m.groups()[0])
				f = ctx.guild.get_member(u_id).display_name
			else:
				match = discord.utils.find(lambda e: f.lower() in e.name.lower() and hasattr(e, 'name'), ctx.guild.members)
				if match:
					f = match.display_name

			fighters[f] = 20
		
		if len(fighters) == 1:
			await ctx.respond("You can't fight yourself??")
			return

		attacks = [
			'{f} uses a rock!',
			'{f} tries to run away!',
			'{f} uses his brain!',
			'{f} falls in love!',
			'{f} calls upon the soul of a dead warrior',
			'{f} falls asleep (zzz)',
			'{f} uses hacks!',
			'{f} need to go to the restroom!',
			'{f} fainted',
			'{f} is hungry??',
			'{f} farted',
			'{f} uses a tnt trap',
			'{f} is lagging',
			'{f} spams fireballs!'
		]

		effects = [
			('It\'s an instant kill!!', 10000),
			('It\'s very effective!', 10),
			('It did the job', 5),
			('It almost worked!', 3),
			('It could hurt a fly', 1),
			('It was useless...', 0)
		]

		round_embed = {
			"type": "rich",
			"title": 'Discord fight',
			"description": '> Round {i}',
			"color": 0x0000FF,
			"fields": [
				{
					"name": 'player1',
					"value": 'attacks',
					"inline": True
				},
				{
					"name": 'player2',
					"value": 'attack too',
					"inline": True
				},
			]
		}

		win_embed = {
			"type": "rich",
			"title": '{f} won!',
			"description": 'With {h}hp left!',
			"color": 0x0000FF,
			"footer": {
				"text": '> use .fight to start another fight!'
			}
		}

		draw_embed = {
			"type": "rich",
			"title": 'Everybody died!',
			"description": 'Because no one won?',
			"color": 0x0000FF,
			"footer": {
				"text": 'use .fight to start another fight!'
			}
		}

		game_embeds = []
		rounds = []
		
		while len(fighters) > 1:
			fight = []
			for fighter in fighters:
				target, health = random.choice([(f,h) for f, h in fighters.items() if f != fighter and h > 0])
				title = f'{fighter} chooses to attack {target}!'

				atk = random.choice(attacks)
				eff, dmg = random.choice(effects)
				txt = f"{atk.format(f=fighter)} \n- {eff} ({dmg}hp):\n {target} now have {health-dmg}hp!"
				
				fighters[target] = health-dmg
				fight.append((title, txt))
				
				# await msg.channel.send(title)
				# await msg.channel.send(txt)
			fighters = {f: h for f, h in fighters.items() if h > 0}

			rounds.append(fight)

		for i, r in enumerate(rounds):
			fields = []
			for title, txt in r:
				fields.append({
					"name": title,
					"value": txt,
					"inline": True
					})
			round_embed["fields"] = fields
			round_embed["description"] = f"Round {i+1}"
			emd = discord.Embed.from_dict(round_embed)
			game_embeds.append(emd)

		if len(fighters) == 1:
			winner, health = list(fighters.items())[0]
			win_embed['title'] = win_embed['title'].format(f=winner)
			win_embed['description'] = win_embed['description'].format(h=health)

			emd = discord.Embed.from_dict(win_embed)
			game_embeds.append(emd)
		else: #len(fighters) == 0
			emd = discord.Embed.from_dict(draw_embed)
			game_embeds.append(emd)

		await ctx.respond(embeds=game_embeds)

	async def kill(self, 
		ctx,
		target : Option(
			discord.Member,
			"The target to kill",
			name="target"),
		):
		"Try to kill someone, but you might get killed yourself!: \n > .kill @user"

		delay = time.time() + 3*60 # 3min

		if target.id == ctx.author.id:
			await ctx.respond(f'{target.mention} suicided! - (Muted for 3m)')
			self.banned_list[target.id] = (delay, 'Suicide')
			return

		if random.choice([True, False]):
			if target.id == self.user.id:
				await ctx.respond(f'{ctx.author.mention} tried to kill {self.user.display_name}, but it was too powerful!')
			else:
				await ctx.respond(f'{target.mention} has been killed by {ctx.author.mention}! - (Muted for 3m)')
				self.banned_list[target.id] = (delay, f'Killed by {ctx.author.display_name}')
		else:
			await ctx.respond(f'Oh no! {ctx.author.mention} was killed while trying to assassinate {target.display_name} - (Muted for 3m)')
			self.banned_list[ctx.author.id] = (delay, f'Killed while trying to assassinate {target.display_name}')

	async def suicide(self, 
		ctx
		):
		"Kill yourself: \n > .suicide"

		delay = time.time() + 3*60 # 3min

		await ctx.respond(f'{ctx.author.mention} suicided! - (Muted for 3m)')
		self.banned_list[ctx.author.id] = (delay, 'Suicide')


module_class = Random