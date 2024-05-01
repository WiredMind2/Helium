import asyncio
import logging
# import logging.handlers
import re
import time
from inspect import signature
import aiohttp

import discord
from discord.ext import commands

from classes import CustomContext, MappingError

logger = logging.getLogger('helium_logger')

# Decorator for command events execution
async_decorator = True
if async_decorator:
    def event(name):  # Event name
        def decorator(func):  # Actual decorator (@)
            async def inner(self, *args, **kwargs):  # Actual processing
                coros = []
                for event in self.events.get(name, []):
                    f = event(*args, **kwargs)
                    if asyncio.iscoroutine(f):
                        coros.append(f)

                wrapped = func(self, *args, **kwargs)
                if asyncio.iscoroutine(wrapped):
                    coros.append(wrapped)

                return await asyncio.gather(*coros)
                # return wait_coros(coros)
            return inner
        return decorator

else:
    def event(name):  # Event name
        def decorator(func):  # Actual decorator (@)
            def inner(self, *args, **kwargs):  # Actual processing
                coros = []

                for event in self.events.get(name, []):
                    f = event(*args, **kwargs)
                    if asyncio.iscoroutine(f):
                        coros.append(f)

                wrapped = func(self, *args, **kwargs)
                if asyncio.iscoroutine(wrapped):
                    coros.append(wrapped)

                return asyncio.gather(*coros)
                # return wait_coros(coros)
            return inner
        return decorator


class Bot_Events:

    @event('on_ready')
    async def on_ready(self):
        logger.info(
            f'{self.user} is ready!, ping: {round(self.latency*1000)}ms')
        await self.get_session()

    async def on_connect(self):
        logger.info(f'{self.user} is connected!')
        await self.get_session()

    async def on_disconnect(self):
        logger.info(f'{self.user} disconnected!')
        await self.get_session(close=True)

    async def on_interaction_wrapper(self, interaction):
        if not self.is_admin(interaction.user) and interaction.user.id in self.banned_list:
            delay, reason = self.banned_list[interaction.user.id]
            if delay is not None and delay < time.time():
                logger.info(
                    f'Unbanned {interaction.user.display_name} - time\'s up!')
                del self.banned_list[interaction.user.id]
            else:
                return

        try:
            await self.process_application_commands(interaction)
        except Exception as e:
            ctx = await self.get_application_context(interaction)
            logger.error('Error: Unknown error: {e}')
            await ctx.respond('An error occured!')

        if interaction.type == discord.InteractionType.application_command:
            txt = f'/{interaction.data["name"]}' + (' ' + ' '.join(
                f"({discord.SlashCommandOptionType(opt['type']).name}, {opt['value']})" for opt in interaction.data['options']) if 'options' in interaction.data else '')

            if interaction.channel.type in (discord.ChannelType.private, discord.ChannelType.group):
                if isinstance(interaction.channel, discord.PartialMessageable) or interaction.channel.recipient is None:
                    logger.info(
                        f'Unidentified DMChannel, id {interaction.channel.id} - {interaction.user.display_name}: {txt}')
                else:
                    logger.info(
                        f'{interaction.channel.recipient.display_name}\'s DMs - {interaction.user.display_name}: {txt}')
            else:
                logger.info(
                    f'{interaction.guild.name} / {interaction.channel.name} - {interaction.user.display_name}: {txt}')

    @event('on_message')
    async def on_message_wrapper(self, msg):
        running = await self.on_message_evt(msg)
        if running is False:
            return
        try:
            await self.process_commands(msg)

        except discord.ext.commands.errors.CommandNotFound as e:
            logger.error(f'Error: Command not found: {e}')

        except discord.ext.commands.errors.BadArgument as e:
            ctx = await self.get_context(msg)
            logger.error(f'Error: Invalid argument: {e}')
            await ctx.respond('Invalid argument!')

        except Exception as e:
            ctx = await self.get_context(msg)
            logger.error(f'Error: Unknown error: {e}')
            await ctx.respond('An error occured!')

    @event('on_application_command_error')
    async def on_application_command_error(self, ctx, e):
        logger.error(
            f'Error on application command - guild: {ctx.guild.name} / channel: {ctx.channel.name} / msg: {ctx.message.content} / command: {ctx.command.qualified_name}: {type(e)} / {str(e)}')
        await ctx.respond('Sorry, an error happened...')

    @event('on_command_error')
    async def on_application_command_error(self, ctx, e):
        logger.error(
            f'Error on command - guild: {ctx.guild.name} / channel: {ctx.channel.name} / msg: {ctx.message.content} / command: {ctx.command.qualified_name}: {type(e)} / {str(e)}')
        await ctx.respond('Sorry, an error happened...')

    @event('on_error')
    async def on_error(e, *args, **kwargs):
        logger.error(f'System error: {e} - args{args} / kwargs{kwargs}')
        
    async def on_message_evt(self, msg):  # '_evt' to prevent override
        if self.user == msg.author:
            return

        if msg.author.bot:
            # mee6 = msg.guild.get_member_named('MEE6#4876')
            # if mee6 is not None and msg.author.id == mee6.id:
            if msg.author.id == 159985870458322944:
                for member in msg.mentions:
                    await self.update_single_role(msg, member)
            return

        if len(msg.embeds) > 0:
            for emb in msg.embeds:
                logger.info(f'{msg.author.display_name}: {emb.to_dict()}')

        if not self.is_admin(msg.author) and msg.author.id in self.banned_list:
            delay, reason = self.banned_list[msg.author.id]
            if delay is not None and delay < time.time():
                logger.info(
                    f'Unbanned {msg.author.display_name} - time\'s up!')
                del self.banned_list[msg.author.id]
            else:
                # chat_input_command = application_command -> slash commands ?
                # thread_created -> thread created from old msgs ?
                if msg.type in (
                        discord.MessageType.default,
                        discord.MessageType.reply,
                        discord.MessageType.application_command
                ):
                    await msg.delete()
                    logger.info(
                        f'DELETED - {msg.author.display_name}: {msg.content}')
                    return False
                else:
                    logger.log('Unknown message type:', msg.type)

        # if msg.content.startswith(self.prefix) and msg.content != self.prefix:
        # 	await self.on_message_cmds(msg)
        # else:
        if msg.author.id in self.parrot_list and msg.content != "":
            await msg.channel.send(msg.content, reference=msg)

        if msg.channel.type in (discord.ChannelType.private, discord.ChannelType.group):
            if msg.channel.recipient is not None:
                logger.info(
                    f'{msg.channel.recipient.display_name}\'s DMs - {msg.author.display_name}: {msg.content}')
            else:
                logger.info(
                    f'Unidentified DMChannel, id {msg.channel.id} - {msg.author.display_name}: {msg.content}')
        else:
            logger.info(
                f'{msg.guild.name} / {msg.channel.name} - {msg.author.display_name}: {msg.content}')

    async def on_message_cmds(self, msg):
        # Not used
        cmd = self.smart_split(msg.content[len(self.prefix):])

        if cmd[0] in self.cmds:
            logger.info(
                f'{msg.author.display_name} used the command: {msg.content}')
            f = self.cmds[cmd[0]]

            args = cmd[1:]
            ctx = await self.get_context(msg, cls=CustomContext)
            await self.invoke(ctx)
            sig = signature(f)
            kwargs = {}

            params = iter(sig.parameters.items())
            for k, p in params:
                if p.annotation == discord.Context:
                    kwargs[k] = ctx

                else:
                    if len(args) != 0:
                        arg = args.pop(0)
                    else:
                        arg = None
                    try:
                        kwargs[k] = await self.format_arg(ctx, arg, p.annotation)
                    except MappingError as e:
                        await ctx.respond(e)
                        return

                    # logger.info(await commands.run_converters(ctx, ))
                    # logger.info(p.annotation, dir(p.annotation), p.annotation.converter, p.annotation.input_type)

            # At least one parameter and args not yet parsed
            if len(sig.parameters) > 0 and len(args) > 0:
                arg = arg + ' ' + ' '.join(args)
                try:
                    kwargs[k] = await self.format_arg(ctx, arg, p.annotation)
                except MappingError as e:
                    await ctx.respond(e)
                    return

            await f(**kwargs)

        else:
            logger.info(
                f'{msg.author.display_name} used an unknown command: {cmd[0]}')

    async def format_arg(self, ctx, arg, annotation):
        def get_member(ctx, arg):
            if arg is None:
                return None

            m = re.match(r'<@!?(\d{17,19})>', arg)
            if m:
                u_id = int(m.groups()[0])
                return ctx.guild.get_member(u_id)

            else:
                logger.warn(
                    f"Can't convert '{arg}' to discord.Member: {arg} - {m}")
                raise MappingError(f"Can't convert '{arg}' to discord.Member")

        format_map = {
            3: lambda ctx, arg: arg,  # str
            4: lambda ctx, arg: int(arg),  # int
            5: lambda ctx, arg: arg.lower() in ('true', 't', '1', 'vrai', 'v', 'o', 'oui'),  # bool
            6: commands.MemberConverter().convert,  # user / member
            7: commands.GuildChannelConverter().convert,  # channel
            8: commands.RoleConverter().convert,  # role
            9: commands.ObjectConverter().convert,  # mentionable (user / role)
            10: lambda ctx, arg: float(arg),  # float
        }

        input_type = annotation.input_type
        hi, lo = annotation.max_value, annotation.min_value
        required = annotation.required
        choices = annotation.choices

        if arg is None:
            if not required:
                return annotation.default
            else:
                raise MappingError(f"Field '{annotation.name}' is required")

        try:
            val = format_map[input_type.value](ctx, arg)
        except Exception as e:
            raise MappingError(str(e))
            # raise MappingError(f"Can't convert '{arg}' to {input_type.name}")

        if asyncio.iscoroutine(val):
            val = await val

        if val is None:
            if not required:
                return annotation.default
            else:
                raise MappingError(f"Field '{annotation.name}' is required")

        if hi is not None and hi < val:
            raise MappingError(f"{val} must be smaller than {hi}")

        if lo is not None and lo > val:
            raise MappingError(f"{val} must be higher than {lo}")

        if len(choices) > 0 and val not in (c.value for c in choices):
            raise MappingError(
                f"Allowed values are: {'/'.join(map(lambda e: str(e.value), choices))} - (got {val})")

        return val

    def smart_split(self, txt, sep=" "):
        out = []
        cur = ''
        in_quotes = False
        for c in txt:
            if c == '"':
                in_quotes = not in_quotes

            elif not in_quotes and c == sep:
                if len(cur) > 0:
                    out.append(cur)
                    cur = ''

            elif c != sep or in_quotes:
                cur += c
        out.append(cur)
        return out

    @event('on_typing')
    async def on_typing(self, channel, user, when):
        # logger.info(f'{user.display_name} is typing in {channel.name}')
        pass

    @event('on_message_edit')
    async def on_message_edit(self, before, after):
        if before.channel.type in (discord.ChannelType.private, discord.ChannelType.group):
            if before.channel.recipient is not None:
                logger.info(
                    f'Edited in user {before.channel.recipient.display_name}\' DMs: {before.content} > {after.content}')
            else:
                logger.info(
                    f'Edited in unidentified DMChannel, id {before.channel.id}: {before.content} > {after.content}')
        else:
            logger.info(
                f'Edited in channel {before.channel.name}, guild {before.guild.name}: {before.content} > {after.content}')

    @event('on_message_delete')
    async def on_message_delete(self, msg):
        if msg.channel.id in self.bot_mode and not msg.author.bot:
            return
        if not self.is_admin(msg.author) and msg.author.id in self.banned_list:
            return
        content = msg.content
        if len(msg.attachments) > 0:
            content += '\n - Attachments: ' + \
                '\n - '.join(
                    map(lambda e: f'{e.filename}: {e.url} / {e.proxy_url}', msg.attachments))
        logger.info(
            f'A message was deleted in channel {msg.channel.name}, guild {msg.guild.name}: {content}')

    @event('on_reaction_add')
    async def on_reaction_add(self, reaction, user):
        logger.info(
            f'{user.display_name} added a reaction on {reaction.message.author}: {reaction.message.content}')

    @event('on_reaction_remove')
    async def on_reaction_remove(self, reaction, user):
        logger.info(
            f'{user.display_name} removed a reaction on {reaction.message.author}: {reaction.message.content}')

    @event('on_member_join')
    async def on_member_join(self, member):
        logger.info(
            f'{member.display_name} just joined the guild {member.guild.name}!')

    @event('on_reaction_remove')
    async def on_member_remove(self, member):
        logger.info(
            f'{member.display_name} just left the guild {member.guild.name}!')

    @event('on_member_update')
    async def on_member_update(self, before, after):
        ignore = ['get_relationship']
        keys = ['activities', 'mobile_status', 'display_name', 'nick', 'name',
                'pending', 'roles', 'desktop_status', 'web_status', 'status']
        changes = {k: getattr(after, k) for k in keys if getattr(
            before, k) != getattr(after, k)}
        # logger.info(f'{after.name} just changed his profile on {after.guild.name}, changes:{changes}')

    @event('on_user_update')
    async def on_user_update(self, before, after):
        keys = ['avatar', 'name', 'display_name', 'discriminator']
        changes = {k: getattr(after, k) for k in keys if getattr(
            before, k) != getattr(after, k)}
        logger.info(
            f'{after.display_name} just changed his user, changes:{changes}')

    @event('on_guild_role_create')
    async def on_guild_role_create(self, role):
        logger.info(f'New role created in guild {role.guild}: {role.name}')

    @event('on_guild_role_delete')
    async def on_guild_role_delete(self, role):
        logger.info(f'New role removed in guild {role.guild}: {role.name}')

    @event('on_member_ban')
    async def on_member_ban(self, guild, user):
        logger.info(
            f'User {user.display_name} was banned from the guild {guild.name}')

    @event('on_member_unban')
    async def on_member_unban(self, guild, user):
        logger.info(
            f'User {user.display_name} was unbanned from the guild {guild.name}')

    @event('on_invite_create')
    async def on_invite_create(self, invite):
        logger.info(
            f'A new invite has been created for guild {invite.guild.name} by {invite.inviter.display_name}')
