#Discord_bot.py admin module

import discord
from discord.ext import commands
from discord.commands.options import Option

import asyncio
import time
import logging
logger = logging.getLogger('helium_logger')
import re
from datetime import datetime, timedelta

class Admin:
	"""Admin stuff: admin"""
	def initialize(self):
		txt_cmds = {
			self.block: ['ban', 'block', 'mute'],
			self.unban: ['unban', 'pardon'],
			self.banned: ['banned'],
			self.block_role: ['role_ban'],
			self.delete: ['del', 'delete', 'purge', 'remove', 'rm'],
			self.rename: ['nick', 'rename'],
			self.rename_all: ['rename_all'],
			self.get_link: ['invite', 'link', 'share'],
			self.set_activity: ['activity', 'set_activity'],
			self.set_status: ['set_status', 'status'],
			self.stop: ['stop']
		}

		# for self.block():
		if not hasattr(self, 'banned_list'):
			self.banned_list = {}

		return txt_cmds

	@discord.option(
		"user",
		description="The user to ban"
	)
	@discord.option(
		"delay",
		description="The delay before unbanning (5sec/2h/5days/...)"
	)
	@discord.option(
		"reason",
		description="The reason for this ban"
	)
	async def block(self, 
		ctx,
		user : discord.Member,
		delay : str,
		reason : str = None
		):
		"Mute someone:\n > .ban @user (5sec/2h/5days/...)"

		if delay is not None:
			try:
				amount, unit, length = self.get_block_delay(delay)
			except Exception as e:
				amount = None

			if amount is None:
				await ctx.respond(f'{delay} has not been recognized as a valid delay!')
				return
		else:
			# Shouldn't happen anymore
			await ctx.respond('You must specify a delay!')
			return
			amount, unit, length = None, None, None

		if not isinstance(user, discord.Member):
			if isinstance(user, discord.User):
				user = ctx.guild.get_member(user.id)

			if not isinstance(user, discord.Member):
				await ctx.respond('Member not found!')
				return

		if not self.is_admin(ctx.author) and ctx.author.top_role.position < user.top_role.position:
			await ctx.respond(f'You can\'t ban someone with a higher rank than you!')
			return

		if length is not None:
			l_txt = f' ({amount} {unit})'
		else:
			l_txt = ''

		if reason is not None:
			r_txt = f' - {reason}'
		else:
			r_txt = ''

		self.banned_list[user.id] = (length, reason)
		
		await ctx.respond(f"{user.display_name}: **BANNED**{l_txt}{r_txt}")

	async def block_role(self, 
		ctx,
		role : Option(
			discord.Role,
			"The role to ban",
			name="user"),
		delay : Option(
			str,
			"The delay before unbanning (5sec/2h/5days/...)",
			name="delay",
			default=None)=None,
		reason : Option(
			str,
			"The reason of this ban",
			name="reason",
			default=None)=None
		):
		"Mute everyone having a role:\n > .ban @role (5sec/2h/5days/...)"

		coros = []
		for member in role.members:
			c = self.block(ctx, member, delay, reason)
			coros.append(c)

		await asyncio.gather(*coros)
		await ctx.respond(f'Banned all members with role: {role.name}')

	def get_block_delay(self, arg):
		units = {
			'month': 30,
			'day': 24,
			'hour': 60,
			'minute': 60,
			'second': 1
		} # Unit name and how many time the precedent one

		units = list(units.items())
		for i, d in reversed(list(enumerate(units))):
			k, v = d
			if i < len(units)-1:
				v = units[i+1][1] * v
			units[i] = (k, v)

		units = dict(units) # Units in seconds

		unit_conv = {
			'month': ['month', 'months'],
			'day': ['d', 'day', 'days'],
			'hour': ['h', 'hour', 'hours', 'hr'],
			'minute': ['m', 'min', 'mins', 'minute', 'minutes'],
			'second': ['s', 'sec', 'secs', 'second', 'seconds']
		}

		unit_conv = {k:v for v, keys in unit_conv.items() for k in keys} # Reversed dict

		amount, unit, length = None, None, None
		if arg is not None:
			rgx = re.compile(r'(\d+)(\w+)')
			m = re.match(rgx, arg)
			if m:
				amount, unit = m.groups()
				amount, unit = int(amount), unit_conv[unit]
				length = int(amount) * units[unit]
				length += time.time()

		return amount, unit, length

	async def unban(self, 
		ctx,
		user : Option(
			discord.Member,
			"The user to ban",
			name="user"),
		reason : Option(
			str,
			"The reason of this unban",
			name="reason",
			default=None)=None
		):
		"Unban someone:\n > .unban @user"

		if not isinstance(user, discord.Member):
			if isinstance(user, discord.User):
				user = ctx.guild.get_member(user.id)

			if not isinstance(user, discord.Member):
				await ctx.respond('Member not found!')
				return

		if not self.is_admin(ctx.author) and ctx.author.top_role.position < user.top_role.position:
			await ctx.respond(f'You can\'t unban someone with a higher rank than you!')
			return

		if user.id == ctx.author.id and not self.is_admin(user.id):
			await ctx.respond(f'You can\'t unban yourself!')
			return

		if reason is None:
			r_txt = ''
		else:
			r_txt = f' - {reason}'

		if user.id in self.banned_list:
			del self.banned_list[user.id]
			await ctx.respond(f"{user.display_name}: **UNBANNED**{r_txt}")

		else:
			await ctx.respond(f"{user.display_name} isn't banned!")

	async def banned(self, 
		ctx,
		user : Option(
			discord.Member,
			"The banned user",
			name="user",
			default=None)=None
		):
		"Check if a user if banned:\n > .banned @user"

		if user is None:
			ids = set(self.banned_list)

			fields = []
			async for member in ctx.guild.fetch_members():
				if member.id in ids:
					data = self.get_banned_text(member, embed=True)
					fields.append(data)

			if fields == []:
				embed = {
					"type": "rich",
					"title": 'No one is currently banned!',
					"description": 'Everybody can speak their mind freely!',
					"color": 0x0000FF,
					"footer": {
						'text': 'Use .ban to temporarily ban someone'
					}
				}
			else:
				if len(fields) == 1:
					desc = 'One person is currently banned'
				else:
					desc = f'{len(fields)} peoples are currently banned:'

				embed = {
					"type": "rich",
					"title": f'Bans on {ctx.guild.name}',
					"description": desc,
					"color": 0x0000FF,
					"fields": fields,
					"footer": {
						'text': 'Use .unban to unban someone'
					}
				}

			embed = discord.Embed.from_dict(embed)
			await ctx.respond(embed=embed)
		else:
			txt = self.get_banned_text(user)
			await ctx.respond(txt)

	def get_banned_text(self, user, embed=False):
		if user.id in self.banned_list:
			delay, reason = self.banned_list[user.id]
			if delay is None:
				l_txt = ''
			else:
				delta = delay - time.time()
				days, delta = divmod(delta, 24*60*60)
				hours, delta = divmod(delta, 60*60)
				mins, secs = divmod(delta, 60)
				days, hours, mins, secs = list(map(int, (days, hours, mins, secs)))
				if days > 0:
					l_txt = f'{days}d {hours}h'
				elif hours > 0:
					l_txt = f'{hours}h{mins}m'
				else:
					l_txt = f'{mins}m{secs}s'
				l_txt += ' left'

			if reason is None:
				r_txt = ''
			else:
				r_txt = f' - {reason}'

			if embed:
				return {
					'name': user.display_name,
					'value': f"**BANNED** {l_txt}{r_txt}"
				}
			else:
				return f"{user.display_name} is currently: **BANNED** {l_txt}{r_txt}"
		else:
			if embed:
				return {
					'name': user.display_name,
					'value': f"**UNBANNED**"
				}
			else:
				return f"{user.display_name} is currently: **UNBANNED**"

	async def rename(self, 
		ctx,
		name : Option(
			str,
			"The new name",
			name="name",
			default=None) = None,
		user : Option(
			discord.Member,
			"The user to rename", 
			name="user",
			default=None) = None
		):
		"Rename someone, leave empty to reset: .nick Helium @Helium"

		if user is None:
			user = ctx.author

		old_name = user.display_name

		if name.lower() in ('none', 'reset'):
			name = None

		try:
			await user.edit(nick=name)
		except discord.Forbidden as e:
			logger.error(e)
			await ctx.respond("I don't have the 'Manage Nicknames' permission!")
		except Exception as e:
			logger.warn(f'Error while renaming {user.display_name}: {e}')
			await ctx.respond('Error')
		else:
			if name is None:
				name = user.name
			await ctx.respond(f'Renamed {old_name} to {name}')

	async def rename_all(self,
		ctx,
		name : Option(
			str,
			"The new name",
			name="name",
			default=None) = None,
		):
		"Rename everyone on the guild (admin only)"

		async def no_error_rename(user, name):
			try:
				await user.edit(nick=name)
			except discord.Forbidden as e:
				logger.error(e)
				# await ctx.respond("I don't have the 'Manage Nicknames' permission!")
			except Exception as e:
				logger.warn(f'Error while renaming {user.display_name}: {e}')
				# await ctx.respond('Error')

		if not self.is_admin(ctx.author):
			await ctx.respond('This is an admin only command!')
			return

		await ctx.defer()

		coros = []
		async for user in ctx.guild.fetch_members():
			if user.nick != name:
				c = no_error_rename(user, name)
				coros.append(c)

		await asyncio.gather(*coros)

		await ctx.respond('Renamed all users!')

	async def delete(self, 
		ctx,
		from_user : Option(
			discord.User,
			"Only delete messages from this user", 
			name="from",
			default=None) = None,
		msg_id : Option(
			str,
			"The id of the message to delete from",
			name="msg_id",
			default=None) = None
		):
		"Purge all messages sent after the referenced message (from user):\n > .purge (@user)\n(Admin only!)"
		
		if not self.is_admin(ctx.author):
			await ctx.respond('Only the bot\'s admin can use this command!')
			return

		if not ctx.channel.permissions_for(ctx.author).manage_messages:
			await ctx.respond("You don't have the 'Manage Messages' permission!")
			return

		ref = ctx.message.reference
		if msg_id is not None:
			msg = await ctx.fetch_message(msg_id)
		elif ref is not None and ref.resolved is not None:
			msg = ref.resolved
		else:
			await ctx.respond('You must specify a message id or reference as starting point!')
			return

		if msg is not None:
			beginning = msg.created_at
		else:
			# TODO - maybe use history()?
			await ctx.respond('Could not find the message!')
			return

		if from_user is not None:
			check = lambda e: e.id != ctx.message.id and e.author.id == from_user.id
		else:
			check = lambda e: e.id != ctx.message.id

		try:
			a = ctx.channel.purge(check=check, after=beginning)	
			b = msg.delete()
			await asyncio.gather(a, b)
		except discord.Forbidden:
			await ctx.respond("I don't have the 'Manage messages' permission!")
			return
		except discord.HTTPException as e:
			logger.warn(f"Error while purging the messages: {e}")
			await ctx.respond("Error while purging the messages")
			return

		# TODO - discord.utils.format_dt()
		date_txt = beginning.strftime('%d %b %Y, %H:%M')
		await ctx.channel.send(f'Purged all messages since {date_txt}')

	async def get_link(self, 
		ctx,
		):
		"Please invite Helium in your server!"
		
		# TODO - discord.utils.oauth_url()
		link = "https://discord.com/api/oauth2/authorize?client_id=720860720509485088&permissions=8&scope=bot"
		await ctx.respond(f'Use this link to add me to your server! \n {link}')

	async def set_status(self, msg, *args):
		# "Allow to change Helium's status (check the API):\n > .status on field1 value1 field2 value2"
		if len(args) == 0:
			args.append("default")

		status_list = {
			discord.Status.online: ['online', 'default', 'on', 'green'],
			discord.Status.offline: ['offline', 'off', 'blank', 'none', None],
			discord.Status.idle: ['idle', 'moon', 'orange', 'sleep', 'sleeping'],
			discord.Status.dnd: ['dnd', 'stop', 'red'],
		}

		status_list = {n:s for s, names in status_list.items() for n in names}

		a = msg.channel.send(f"Settings status to {args[0]} - {status_list[args[0]]}")
		b = self.change_presence(status=status_list[args[0]])
		await asyncio.gather(a, b)

	async def set_activity(self, msg, *args):
		if len(args) == 0:
			args.append("default")

		activity_list = {
			discord.Game: {
				'txt': ['game', 'play'],
				'args': ['name'],
				'force': ['name']
			},
			discord.Streaming: {
				'txt': ['streaming', 'stream'],
				'args': ['platform', 'name', 'game', 'url'],
				'force': ['name', 'url']
			},
			discord.CustomActivity: {
				'txt': ['custom', 'special'],
				'args': ['name'],
				'force': ['name']
			},
			None: {
				'txt': ['default', 'none', None],
				'args': []
			}
		}

		txts = {txt: (act, data) for act, data in activity_list.items() for txt in data['txt']}

		action, *args = args

		if action not in txts:
			await msg.channel.send(f'Unknown activity: {action}')
			return

		act, data = txts[action]
		args = {args[i]:args[i+1] for i in range(0, len(args), 2)}
		for arg in args:
			if arg not in data['args']:
				await msg.channel.send(f'Invalid argument: {arg}!')
				return

		act = act(**args)

		a = msg.channel.send(f"Updating activity!")
		b = self.change_presence(activity=act)
		await asyncio.gather(a, b)

	async def stop(self, msg, *args):
		if not self.is_admin(msg.author):
			await msg.channel.send("You are not allowed to stop the bot!")
			return
		await msg.channel.send("Bye!")
		await msg.channel.send("*Shutting down...*")
		await self.close()
		# self.exit_handler()
		exit()


module_class = Admin