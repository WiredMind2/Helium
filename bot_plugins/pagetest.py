# Docs: https://docs.pycord.dev/en/master/ext/pages/index.html
# Note that the below examples use a Slash Command Group in a cog for better organization - it's not required for using ext.pages.
import asyncio

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages as extpages

import sys, os

if __name__ == "__main__":

    bot = commands.Bot(prefix='.')

    pages = [
        "Page 1",
        [
            discord.Embed(title="Page 2, Embed 1"),
            discord.Embed(title="Page 2, Embed 2"),
        ],
        "Page Three",
        discord.Embed(title="Page Four"),
        discord.Embed(title="Page Five"),
        [
            discord.Embed(title="Page Six, Embed 1"),
            discord.Embed(title="Page Seven, Embed 2"),
        ],
    ]
    pages[3].set_image(url="https://c.tenor.com/pPKOYQpTO8AAAAAM/monkey-developer.gif")
    pages[4].add_field(name="Example Field", value="Example Value", inline=False)
    pages[4].add_field(name="Another Example Field", value="Another Example Value", inline=False)

    more_pages = [
        "Second Page One",
        discord.Embed(title="Second Page Two"),
        discord.Embed(title="Second Page Three"),
    ]

    even_more_pages = ["11111", "22222", "33333"]

    new_pages = [
        extpages.Page(
            content="Page 1 Title!",
            embeds=[
                discord.Embed(title="New Page 1 Embed Title 1!"),
                discord.Embed(title="New Page 1 Embed Title 2!"),
            ],
        ),
        extpages.Page(
            content="Page 2 Title!",
            embeds=[
                discord.Embed(title="New Page 2 Embed Title 1!"),
                discord.Embed(title="New Page 2 Embed Title 2!"),
            ],
        ),
    ]

    def get_pages():
        return pages

    pagetest = SlashCommandGroup("pagetest", "Commands for testing ext.pages")

    # These examples use a Slash Command Group in a cog for better organization - it's not required for using ext.pages.
    @pagetest.command(name="default")
    async def pagetest_default(ctx: discord.ApplicationContext):
        """Demonstrates using the paginator with the default options."""
        paginator = extpages.Paginator(pages=get_pages())
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="new")
    async def pagetest_new(ctx: discord.ApplicationContext):
        """Demonstrates using the paginator with the Page class."""
        paginator = extpages.Paginator(pages=new_pages)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="hidden")
    async def pagetest_hidden(ctx: discord.ApplicationContext):
        """Demonstrates using the paginator with disabled buttons hidden."""
        paginator = extpages.Paginator(pages=get_pages(), show_disabled=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="loop")
    async def pagetest_loop(ctx: discord.ApplicationContext):
        """Demonstrates using the loop_pages option."""
        paginator = extpages.Paginator(pages=get_pages(), loop_pages=True)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="strings")
    async def pagetest_strings(ctx: discord.ApplicationContext):
        """Demonstrates passing a list of strings as pages."""
        paginator = extpages.Paginator(pages=["Page 1", "Page 2", "Page 3"], loop_pages=True)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="timeout")
    async def pagetest_timeout(ctx: discord.ApplicationContext):
        """Demonstrates having the buttons be disabled when the paginator view times out."""
        paginator = extpages.Paginator(pages=get_pages(), disable_on_timeout=True, timeout=30)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="remove_buttons")
    async def pagetest_remove(ctx: discord.ApplicationContext):
        """Demonstrates using the default buttons, but removing some of them."""
        paginator = extpages.Paginator(pages=get_pages())
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="init")
    async def pagetest_init(ctx: discord.ApplicationContext):
        """Demonstrates how to pass a list of custom buttons when creating the Paginator instance."""
        pagelist = [
            extpages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            extpages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]
        paginator = extpages.Paginator(
            pages=get_pages(),
            show_disabled=True,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=pagelist,
            loop_pages=True,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="custom_buttons")
    async def pagetest_custom_buttons(ctx: discord.ApplicationContext):
        """Demonstrates adding buttons to the paginator when the default buttons are not used."""
        paginator = extpages.Paginator(
            pages=get_pages(),
            use_default_buttons=False,
            loop_pages=False,
            show_disabled=False,
        )
        paginator.add_button(
            extpages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green, loop_label="lst")
        )
        paginator.add_button(extpages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True))
        paginator.add_button(extpages.PaginatorButton("next", style=discord.ButtonStyle.green, loop_label="fst"))
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="emoji_buttons")
    async def pagetest_emoji_buttons(ctx: discord.ApplicationContext):
        """Demonstrates using emojis for the paginator buttons instead of labels."""
        page_buttons = [
            extpages.PaginatorButton("first", emoji="⏪", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("prev", emoji="⬅", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            extpages.PaginatorButton("next", emoji="➡", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("last", emoji="⏩", style=discord.ButtonStyle.green),
        ]
        paginator = extpages.Paginator(
            pages=get_pages(),
            show_disabled=True,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=page_buttons,
            loop_pages=True,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="custom_view")
    async def pagetest_custom_view(ctx: discord.ApplicationContext):
        """Demonstrates passing a custom view to the paginator."""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
        view.add_item(
            discord.ui.Select(
                placeholder="Test Select Menu, Does Nothing",
                options=[
                    discord.SelectOption(
                        label="Example Option",
                        value="Example Value",
                        description="This menu does nothing!",
                    )
                ],
            )
        )
        paginator = extpages.Paginator(pages=get_pages(), custom_view=view)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="disable")
    async def pagetest_disable(ctx: discord.ApplicationContext):
        """Demonstrates disabling the paginator buttons and showing a custom page when disabled."""
        paginator = extpages.Paginator(pages=get_pages())
        await paginator.respond(ctx.interaction, ephemeral=False)
        await ctx.respond("Disabling paginator in 5 seconds...")
        await asyncio.sleep(5)
        disable_page = discord.Embed(
            title="Paginator Disabled!",
            description="This page is only shown when the paginator is disabled.",
        )
        await paginator.disable(page=disable_page)

    @pagetest.command(name="cancel")
    async def pagetest_cancel(ctx: discord.ApplicationContext):
        """Demonstrates canceling (stopping) the paginator and showing a custom page when cancelled."""
        paginator = extpages.Paginator(pages=get_pages())
        await paginator.respond(ctx.interaction, ephemeral=False)
        await ctx.respond("Canceling paginator in 5 seconds...")
        await asyncio.sleep(5)
        cancel_page = discord.Embed(
            title="Paginator Cancelled!",
            description="This page is only shown when the paginator is cancelled.",
        )
        await paginator.cancel(page=cancel_page)

    @pagetest.command(name="groups")
    async def pagetest_groups(ctx: discord.ApplicationContext):
        """Demonstrates using page groups to switch between different sets of pages."""
        page_buttons = [
            extpages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            extpages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            extpages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=2))
        view.add_item(
            discord.ui.Select(
                placeholder="Test Select Menu, Does Nothing",
                options=[
                    discord.SelectOption(
                        label="Example Option",
                        value="Example Value",
                        description="This menu does nothing!",
                    )
                ],
            )
        )
        page_groups = [
            extpages.PageGroup(
                pages=get_pages(),
                label="Main Page Group",
                description="Main Pages for Main Things",
            ),
            extpages.PageGroup(
                pages=[
                    "Second Set of Pages, Page 1",
                    "Second Set of Pages, Page 2",
                    "Look, it's group 2, page 3!",
                ],
                label="Second Page Group",
                description="Secondary Pages for Secondary Things",
                custom_buttons=page_buttons,
                use_default_buttons=False,
                custom_view=view,
            ),
        ]
        paginator = extpages.Paginator(pages=page_groups, show_menu=True)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="update")
    async def pagetest_update(ctx: discord.ApplicationContext):
        """Demonstrates updating an existing paginator instance with different options."""
        paginator = extpages.Paginator(pages=get_pages(), show_disabled=False)
        await paginator.respond(ctx.interaction)
        await asyncio.sleep(3)
        await paginator.update(show_disabled=True, show_indicator=False)

    @pagetest.command(name="target")
    async def pagetest_target(ctx: discord.ApplicationContext):
        """Demonstrates sending the paginator to a different target than where it was invoked."""
        paginator = extpages.Paginator(pages=get_pages())
        await paginator.respond(ctx.interaction, target=ctx.interaction.user)

    @commands.command()
    async def pagetest_prefix(ctx: commands.Context):
        """Demonstrates using the paginator with a prefix-based command."""
        paginator = extpages.Paginator(pages=get_pages(), use_default_buttons=False)
        paginator.add_button(extpages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green))
        paginator.add_button(extpages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True))
        paginator.add_button(extpages.PaginatorButton("next", style=discord.ButtonStyle.green))
        await paginator.send(ctx)

    @commands.command()
    async def pagetest_target(ctx: commands.Context):
        """Demonstrates sending the paginator to a different target than where it was invoked (prefix-command version)."""
        paginator = extpages.Paginator(pages=get_pages())
        await paginator.send(ctx, target=ctx.author, target_message="Paginator sent!")

    @bot.event
    async def on_ready():
        print('yo')

    bot.add_application_command(pagetest)

    sys.path.append(os.path.abspath('../helium'))
    import token_secret

    bot.run(token_secret.helium)