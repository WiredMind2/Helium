
import asyncio
import enum
import os
import sys
import time

from groq import Groq

import aiohttp
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from token_secret import GROQ_API_KEY

class OpenAI:
	def initialize(self):
		# Rate limiting
		self.last_requests = {
			'completions': {'requests': [], 'rate_limit': 20},
			'images': {'requests': [], 'rate_limit': 50},
		}
  
		self.client = AsyncGroq(
			api_key=GROQ_API_KEY,
		)
		self.temperature = 0.0 # TODO ??


	async def rate_limit(self, endpoint): # Not used
		endpoint = endpoint.split('/')[0]
		now = time.time()
		while len(self.last_requests[endpoint]['requests']) > 0 and self.last_requests[endpoint]['requests'][0] < now - 60:
			self.last_requests[endpoint]['requests'].pop(0)
		
		while len(self.last_requests[endpoint]['requests']) > self.last_requests[endpoint]['rate_limit']:
			last = self.last_requests[endpoint]['requests'].pop(0)
			await asyncio.sleep(last + 60 - now)

	# Completions
	async def completion(self, prompt):
		chat_completion = await self.client.chat.completions.create(
			messages=[
				{
					"role": "user",
					"content": prompt,
				}
			],
			model="llama3-8b-8192",
			temperature=self.temperature,
		)
		return chat_completion.choices[0].message.content
