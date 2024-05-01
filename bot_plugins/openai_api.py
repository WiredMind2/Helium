
import asyncio
import enum
import os
import sys
import time

import aiohttp
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from token_secret import CHAT_GPT_API_KEY

class OpenAI:
	def initialize(self):
		
		# Queues for batching:
		self.prompts_queue = []

		# Rate limiting
		self.last_requests = {
			'completions': {'requests': [], 'rate_limit': 20},
			'images': {'requests': [], 'rate_limit': 50},
		}

	async def api_request(self, method, endpoint, json=None, data=None):
		BASE_URL = "https://api.openai.com/v1/"

		url = BASE_URL + endpoint

		headers = {
			'Content-Type': 'application/json',
			'Authorization': f"Bearer {CHAT_GPT_API_KEY}"
		}
		
		await self.get_session()
		
		if method == 'GET':
			async with self.session.get(url, headers=headers) as r:
				data = await r.json()
		elif method == 'POST':
			if data is not None:
				del headers['Content-Type']

			async with self.session.post(url, headers=headers, json=json, data=data) as r:
				data = await r.json()
		else:
			print(f'Invalid method: {method}')
			return None

		return data

	async def rate_limit(self, endpoint):
		endpoint = endpoint.split('/')[0]
		now = time.time()
		while len(self.last_requests[endpoint]['requests']) > 0 and self.last_requests[endpoint]['requests'][0] < now - 60:
			self.last_requests[endpoint]['requests'].pop(0)
		
		while len(self.last_requests[endpoint]['requests']) > self.last_requests[endpoint]['rate_limit']:
			last = self.last_requests[endpoint]['requests'].pop(0)
			await asyncio.sleep(last + 60 - now)

	# Completions
	async def run_completions(self):
		# Respect rate limits
		if len(self.prompts_queue) == 0:
			return
		
		endpoint = 'completions'
		await self.rate_limit(endpoint)

		self.last_requests[endpoint]['requests'].append(time.time())

		queues, prompts = [], []
		for q, p in self.prompts_queue:
			queues.append(q)
			prompts.append(p)

		self.prompts_queue = []

		data = {
			'model': 'text-davinci-003',
			'prompt': prompts,
			'max_tokens': 2000
		}

		r = await self.api_request('POST', endpoint, json=data)
		if r.get('error', None):
			if r['error']['code'] == 'insufficient_quota':
				# Out of tokens
				queues[c['index']].put(OpenAiError.INSUFFICIENT_TOKEN)
				return

		choices = sorted(r['choices'], key=lambda c: c['index'])

		for c in choices:
			await queues[c['index']].put(c)
	
	async def completion(self, prompt):
		que = asyncio.Queue(1)
		self.prompts_queue.append((que, prompt))
		await self.run_completions()
		c = await que.get()
		if c == OpenAiError.INSUFFICIENT_TOKEN:
			return {'error':'Sorry, but I now have to pay in order to bring back Helium\'s chatbot.\nPlease consider donating if you wish to bring it back!'}
		return c

	
	# Images
	async def image_prompt(self, prompt, n=1, size=256):
		# Respect rate limits

		if size not in (256, 512, 1024):
			raise ValueError('Size must be one of 256, 512, 1024')

		endpoint = 'images/generations'
		await self.rate_limit(endpoint)

		for _ in range(n):
			self.last_requests[endpoint.split('/')[0]]['requests'].append(time.time())

		queues, prompts = [], []
		for q, p in self.prompts_queue:
			queues.append(q)
			prompts.append(p)

		self.prompts_queue = []

		data = {
			'prompt': prompt,
			'n': n,
			'size': f'{size}x{size}',
			'response_format': 'url'
		}

		r = await self.api_request('POST', endpoint, json=data)
		return r['data']
	
	async def image_variations(self, image, n=1, size=256):
		# Respect rate limits

		if size not in (256, 512, 1024):
			raise ValueError(f'Size must be one of 256, 512, 1024, not {size}')

		if n < 1 or n > 10:
			raise ValueError(f'n must be between 1 and 10, not {n}')

		endpoint = 'images/variations'
		await self.rate_limit(endpoint)

		for _ in range(n):
			self.last_requests[endpoint.split('/')[0]]['requests'].append(time.time())

		queues, prompts = [], []
		for q, p in self.prompts_queue:
			queues.append(q)
			prompts.append(p)

		self.prompts_queue = []

		data = {
			'image': image,
			'n': str(n),
			'size': f'{256}x{256}',
			'response_format': 'url'
		}

		r = await self.api_request('POST', endpoint, data=data)
		return r['data']


class OpenAiError(enum.Enum):
	INSUFFICIENT_TOKEN = 1


if __name__ == '__main__':
	async def func():
		BASE_URL = "https://api.openai.com/v1/"

		endpoint = 'images/variations'
		url = BASE_URL + endpoint

		headers = {
			'Authorization': f"Bearer {CHAT_GPT_API_KEY}"
		}

		
		
		with open('img.png', 'rb') as image:
			data = {
				'image': image,
				'n': '5',
				'size': f'{256}x{256}',
				'response_format': 'url'
			}
			async with aiohttp.ClientSession() as session:
				async with session.post(url, headers=headers, data=data) as response:
					data = await response.json()
				
					pass
	
	asyncio.run(func())
