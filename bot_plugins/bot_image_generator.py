
import base64
import io
import discord
import logging

from .openai_api import OpenAI
logger = logging.getLogger('helium_logger')


class ImageGenerator(OpenAI):
	"""Image Generator: imggen"""
	def initialize(self):
		super().initialize()
		txt_cmds = {
			self.create_image: ['create_image', 'image'],
			self.variations: ['variations', 'image_variations']
		}

		return txt_cmds
	
	@discord.option(
		"description",
		description="A description of the image",
		required=True
	)
	@discord.option(
		"amount",
		description="The amount of images to generate",
		min_value=1,
		max_value=10
	)
	@discord.option(
		"size",
		description="The size of the generated images",
		choices=[256, 512, 1024]
	)
	async def create_image(self, 
		ctx, 
		description : str,
		amount: int = 1,
		size: int = 256
		):
		"Image generation: describe an image to generate it!\n > .create_image description"

		await ctx.defer()

		try:
			data = await self.image_prompt(description, n=amount, size=size)

			if len(data) == 0:
				await ctx.respond('No image were generated, please try a different description')

			print(data)
			
			embeds = [{
				"type": "rich",
				"title": "Here's your image!" if amount == 1 else f"Here are your {amount} images!",
				"description": f'For: "{description}"',
				"color": 0x0000FF,
				"footer": {
					"text": 'Use `.create_image description` to create another image'
				}
			}]

			embeds += [{
				"type": "rich",
				"color": 0x0000FF,
				"image": {
					"url": img['url'],
					"height": size,
					"width": size
				},

			} for img in data]

			embeds = [discord.Embed.from_dict(e) for e in embeds]
			await ctx.respond(embeds=embeds)
		except Exception as e:
			logger.warn(f'Error while generating image from prompt: {description}: {e}')
			await ctx.respond('There has been an error generating the image')

	@discord.option(
		"amount",
		description="The amount of images to generate",
		min_value=1,
		max_value=10
	)
	@discord.option(
		"size",
		description="The size of the generated images",
		choices=[256, 512, 1024]
	)
	async def variations(self, 
		ctx, 
		# image : str, # TODO - Check for image in reply or smth
		amount: int = 1,
		size: int = 256
		):
		"Image variation: get variations of your pfp!\n > .variations (amount) (size)"

		await ctx.defer()

		try:
			# buff = io.BytesIO()
			img = ctx.author.display_avatar.with_format('png')
			buff = io.BytesIO()
			await img.save(buff)
			data = await self.image_variations(buff, n=amount, size=size)

			if len(data) == 0:
				await ctx.respond('No image were generated, please try again')

			print(data)
			
			embeds = [{
				"type": "rich",
				"title": "Here's your image!" if amount == 1 else f"Here are your {amount} images!",
				"description": f'Variation{"s" if amount > 1 else ""} of {ctx.author.display_name}\'s pfp',
				"color": 0x0000FF,
				"footer": {
					"text": 'Use `.variations (amount) (size)` to create another image'
				}
			}]

			embeds += [{
				"type": "rich",
				"color": 0x0000FF,
				"image": {
					"url": img['url'],
					"height": size,
					"width": size
				},

			} for img in data]

			embeds = [discord.Embed.from_dict(e) for e in embeds]
			await ctx.respond(embeds=embeds)
		except Exception as e:
			logger.warn(f'Error while generating image variation: {ctx.author}: {e}')
			await ctx.respond('There has been an error generating the image')

module_class = ImageGenerator