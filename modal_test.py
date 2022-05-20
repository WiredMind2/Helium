import discord
from discord.ext import commands
from discord.ui import InputText, Modal


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">")


bot = Bot()


class MyModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Short Input", placeholder="Placeholder Test"))

        self.add_item(
            InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.random())
        embed.add_field(name="First Input", value=self.children[0].value, inline=False)
        embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
        await interaction.response.send_message(embeds=[embed])


@bot.slash_command(name="modaltest", guild_ids=[724303646443044995])
async def modal_slash(ctx):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = MyModal(title="Slash Command Modal")
    await ctx.send_modal(modal)


class MyView(discord.ui.View):
    @discord.ui.button(label="B1", style=discord.ButtonStyle.primary, row=1)
    async def button1_callback(self, button, interaction):
        await interaction.response.pong()

    @discord.ui.button(label="B2", style=discord.ButtonStyle.primary, row=1)
    async def button2_callback(self, button, interaction):
        await interaction.response.pong()

    @discord.ui.button(label="B3", style=discord.ButtonStyle.primary, row=1)
    async def button3_callback(self, button, interaction):
        await interaction.response.pong()

    @discord.ui.button(label="B4", style=discord.ButtonStyle.primary, row=2)
    async def button4_callback(self, button, interaction):
        await interaction.response.pong()

    @discord.ui.select(
        placeholder="Pick Your Modal",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="First Modal", description="Shows the first modal"),
            discord.SelectOption(label="Second Modal", description="Shows the second modal"),
        ],
        row=3
    )
    async def select_callback(self, select, interaction):
        modal = MyModal(title="Temporary Title")
        modal.title = select.values[0]
        await interaction.response.send_modal(modal)

@bot.slash_command(name="modaltest2", guild_ids=[724303646443044995])
async def modaltest(ctx):
    """Shows an example of modals being invoked"""# from an interaction component (e.g. a button or select menu)"""

    view = MyView()
    await ctx.send("Click Button, Receive Modal", view=view)

from token_secret import *
bot.run(helium)
