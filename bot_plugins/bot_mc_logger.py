#Discord_bot.py mc logger module

import discord
from discord import ApplicationContext, Option

import socket
import json
import sys
import os
import logging
import subprocess
import multiprocessing
logger = logging.getLogger('helium_logger')

class Minecraft:
	"""Minecraft logger: mc"""
	def initialize(self):
		txt_cmds = {
			self.start_mc_log: ['start_mc_log'],
			self.stop_mc_log: ['stop_mc_log']
		}

		events = {
			'on_message': self.log_msg,
			'on_ready': self.mc_log_autoconnect
		}

		self.sock_addr = ('localhost', 14444)

		if not hasattr(self, 'mc_log_channel'):
			self.mc_log_channel = None

		return txt_cmds, events
	
	async def mc_log_autoconnect(self):
		if self.mc_log_channel is not None:
			try:
				channel = await self.fetch_channel(self.mc_log_channel)
			except Exception as e:
				logger.info(f'Channel not found: {self.mc_log_channel} - {e}')
			else:
				webhook = await self.get_webhook(channel)
				self.start_remote_process(webhook.url)

	async def log_msg(self, msg):
		if self.mc_log_channel is None or msg.channel.id != self.mc_log_channel:
			return

		if len(msg.attachments) > 0:
			return

		if msg.type != discord.MessageType.default:
			return

		if msg.author.bot:
			return

		author = msg.author.display_name
		col_int = msg.author.color.value
		col = "#" + hex(col_int)[2:].upper()
		text = msg.clean_content

		if text != '':
			data = {
				'command': 'chat',
				'author': author,
				'col': col,
				'msg': text
			}
			data = json.dumps(data)

			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				try:
					sock.connect(self.sock_addr)
				except:
					webhook = await self.get_webhook(msg.channel)
					self.start_remote_process(webhook.url)
					sock.connect(self.sock_addr)
				sock.sendall(bytes(data, encoding='utf-8'))			
			except Exception as e:
				logger.warn(f'Error on log_msg: {e}')
			finally:
				sock.close()
	
	async def start_mc_log(self, 
		ctx : ApplicationContext
		):
		"Starts the minecraft logger (admin only)"

		if ctx.author.id != self.admin:
			await ctx.respond('This is an admin only command!')
			return
		
		perms = ctx.channel.permissions_for(ctx.guild.me)
		if not perms.manage_webhooks:
			await ctx.respond("I need the 'Manage Webhooks' permission to log Minecraft messages!")
			return

		self.mc_log_channel = ctx.channel.id

		await ctx.respond(f'Now logging channel {ctx.channel.name} on Minecraft!')

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect(self.sock_addr)
		except:
			try:
				webhook = await self.get_webhook(ctx.channel)
				self.start_remote_process(webhook.url)
				sock.connect(self.sock_addr)
			except Exception as e:
				logger.warn(f'Error on start_mc_log: {e}')
		finally:
			sock.close()

	async def stop_mc_log(self, 
		ctx : ApplicationContext
		):
		"Stops the minecraft logger (admin only)"

		if ctx.author.id != self.admin:
			await ctx.respond('This is an admin only command!')
			return

		data = {
			'command': 'quit'
		}
		data = json.dumps(data)

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect(self.sock_addr)
			sock.sendall(bytes(data, encoding='utf-8'))
		except Exception as e:
			logger.warn(f'Error on stop_mc_log: {e}')
		finally:
			sock.close()
	
	def start_remote_process(self, webhook):

		logger.info('Starting mc bot process')
		multiprocessing.Process(target=remote_process, args=(webhook,), daemon=True).start()

def remote_process(webhook):
	cmd_file_path = "./start_mc_logger." + ('sh' if sys.platform.startswith('linux') else 'bat')
	cmd_file_path = os.path.abspath(cmd_file_path)
	cmd_file_path += ' ' + webhook
	subprocess.run(cmd_file_path, shell=True)


module_class = Minecraft