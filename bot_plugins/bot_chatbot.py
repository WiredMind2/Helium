CHATBOT = "Groq"
if CHATBOT == "OpenAI":
	from .openai_api import OpenAI
	MANAGER = OpenAI
elif CHATBOT == "Groq":
	from .groq_api import Groq
	MANAGER = Groq
 
import discord
import logging
logger = logging.getLogger('helium_logger')


PROMPT_CONTEXT = " \
Helium: I am a discord bot, I have been created by WiredMind, he created me all by himself. \
"


class Chatbot(MANAGER):
	"""Chatbot: chatbot"""

	def initialize(self):
		super().initialize()
		txt_cmds = {
			self.chat_channel: ['chat_channel'],
		}

		events = {
			'on_message': self.chat
		}

		if not hasattr(self, 'chat_channels'):
			self.chat_channels = []

		return txt_cmds, events

	@discord.option(
		"action",
		description="The action to perform",
		choices=["on", "off", "status"],
		required=True
	)
	async def chat_channel(self,
						   ctx,
						   action: str
						   ):
		"Chat channel: talk with Helium! (admin only!)\n > .register_channel (on/off/status)"

		if not self.is_admin(ctx.author):
			await ctx.respond(f'Only admins can use this command!')
			return

		c_id = ctx.channel.id
		if action == 'on':
			if c_id not in self.chat_channels:
				self.chat_channels.append(c_id)
			status = "ENABLED"

		elif action == 'off':
			if c_id in self.chat_channels:
				self.chat_channels.remove(c_id)
			status = "DISABLED"

		elif action == 'status':
			mode = c_id in self.chat_channels
			status = "ENABLED" if mode else "DISABLED"

		await ctx.respond(f'Chatbot: **{status}**')

	async def chat(self, msg):
		if msg.channel.id not in self.chat_channels:
			return

		if msg.author.id == self.user.id:
			return

		if len(msg.attachments) > 0:
			return

		if msg.type not in (discord.MessageType.default, discord.MessageType.reply):
			return

		def filter_mention(content):
			for m in (f"<@{self.user.id}> ", f"<@!{self.user.id}>"):
				if content.startswith(m):
					return content[len(m):]
			return content

		triggered = False
		conv = []
		content = msg.content
		filtered = content

		filtered = filter_mention(content)
		if filtered != content:
			# There was a mention in the msg
			triggered = True

		# suffix = '???'
		if not triggered and msg.type == discord.MessageType.reply and msg.reference is not None:
			if msg.reference.resolved is not None and msg.reference.resolved.author.id == self.user.id:
				# Answer to previous message
				triggered = True

		if triggered:
			# Check if msg isn't actually a command
			ctx = await self.get_context(msg)
			if ctx.command is not None:
				return

			if msg.type == discord.MessageType.reply:
				conv = await self.fetch_conv(msg)

			prompt = PROMPT_CONTEXT + \
				'\n'.join(map(lambda m: f'{m.author.display_name}: {filter_mention(m.content)}',
						  conv)) + f'\n{msg.author.display_name}: {filtered}\n{msg.guild.me.display_name}: '

			# self.prompts_queue.append((msg, prompt))
			# await self.run_completions()

			c = await self.completion(prompt)

			if c['error'] is not None:
				answer = c['error']
			else:
				answer = c['text'].strip()

			logger.info(
				f'{msg.guild.name} / {msg.channel.name} - {msg.guild.me.display_name}: {answer}')
			await msg.reply(answer)

	async def fetch_conv(self, source):
		channel = source.channel

		msg = source
		conv = []

		while msg is not None and msg.reference is not None and len(conv) < 10:
			ref = msg.reference
			msg = ref.cached_message or ref.resolved

			if msg is None:
				try:
					msg = await channel.fetch_message(ref.message_id)
				except Exception as e:
					msg = None

			if isinstance(msg, discord.DeletedReferencedMessage):
				break

			if isinstance(msg, discord.Message):
				conv.append(msg)

		return conv[::-1]


module_class = Chatbot
