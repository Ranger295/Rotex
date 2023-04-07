from statistics import mean, mode
import datetime
import discord
import random
import asyncio
import requests
from discord import Option
from discord.ext import commands
from db_import import db, GROUPS, GUILDS, LINKED, TG_LINKED, WEBHOOKS
from tokens import DS_TOKEN, TG_TOKEN


COMMAND_LIST = "```Общее:``` \n" \
               "`!hey`  -  проверить, жив ли я.\n" \
               "`/help`  -  список команд.\n" \



bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), help_command=None)
activity = discord.Activity(type=discord.ActivityType.watching, name="за сервером")

webhook_1 = ''
webhook_2 = ''
webhook_3 = ''
BOT_IS_READY = False


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return


    if message.author.discriminator != '0000' and (db.get(GUILDS, str(message.guild.id))).TG_LINKED_CHANNELS_ID and \
            str(message.channel.id) in (db.get(GUILDS, str(message.guild.id))).TG_LINKED_CHANNELS_ID:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}"
            tg_chat_id = db.get(TG_LINKED, str(message.channel.id)).LINKED_CHANNEL_ID
            author = []
            for sign in f'{message.author.name}':
                if sign in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                    author.append(f'\{sign}')
                else:
                    author.append(sign)
            author = "".join(author)
            message_author = f"*[{author} 〔DS〕](tg://user?id={bot.user.id})*\n"
            tg_message = []
            if message.content:
                for sign in message.content:
                    if sign in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                        tg_message.append(f'\{sign}')
                    else:
                        tg_message.append(sign)
                tg_message = message_author + "".join(tg_message)
            else:
                tg_message = message_author

            method = url + "/sendMessage"
            r = requests.post(method, data={
                "chat_id": tg_chat_id,
                "text": tg_message,
                "parse_mode": "MarkdownV2"
            })
            if r.status_code != 200:
                raise Exception("ТЕКСТ ЕГГОР! Код НЕ 200!")
            if len(message.attachments) > 0:
                for attach in message.attachments:
                    await attach.save(f'tempdata/{attach.filename}')
                    if attach.content_type:
                        file_type = attach.content_type.split('/')[0]
                    else:
                        file_type = None
                    if file_type == 'image':
                        if attach.filename.endswith('gif'):
                            files = {'animation': open(f'tempdata/{attach.filename}', 'rb')}
                            r = requests.post(url + "/sendAnimation?chat_id=" + tg_chat_id, files=files)
                            if r.status_code != 200:
                                raise Exception("ФОТО ЕГГОР! Код НЕ 200!")
                        else:
                            files = {'photo': open(f'tempdata/{attach.filename}', 'rb')}
                            r = requests.post(url + "/sendPhoto?chat_id=" + tg_chat_id, files=files)
                            if r.status_code != 200:
                                raise Exception("ГИФ ЕГГОР! Код НЕ 200!")
                    elif file_type == 'application' or file_type == 'text' or not file_type:
                        files = {'document': open(f'tempdata/{attach.filename}', 'rb')}
                        r = requests.post(url + "/sendDocument?chat_id=" + tg_chat_id, files=files)
                        if r.status_code != 200:
                            raise Exception("ФАЙЛ ЕГГОР! Код НЕ 200!")
                    elif file_type == 'video':
                        files = {'video': open(f'tempdata/{attach.filename}', 'rb')}
                        r = requests.post(url + "/sendVideo?chat_id=" + tg_chat_id, files=files)
                        if r.status_code != 200:
                            raise Exception("ВИДЕО ЕГГОР! Код НЕ 200!")
                    elif file_type == 'audio':
                        files = {'audio': open(f'tempdata/{attach.filename}', 'rb')}
                        r = requests.post(url + "/sendAudio?chat_id=" + tg_chat_id, files=files)
                        if r.status_code != 200:
                            raise Exception("АУДИО ЕГГОР! Код НЕ 200!")
        except Exception as e:
            print(e)





    if message.author.discriminator != '0000' and (db.get(GUILDS, str(message.guild.id))).LINKED_CHANNELS_ID and \
            str(message.channel.id) in (db.get(GUILDS, str(message.guild.id))).LINKED_CHANNELS_ID:
        # await message.reply(f'Id гильдии: {str(message.guild.id)}\nId канала: {str(message.channel.id)}\nLinked channels id: {(db.get(GUILDS, str(message.guild.id))).LINKED_CHANNELS_ID}\n')
        linked_channels_list = (((db.get(LINKED, str(message.channel.id))).LINKED_CHANNELS_ID).split(':'))
        for channel in linked_channels_list:
            try:
                webhooks = await (bot.get_channel(int(channel))).webhooks()
                webhook_exists = False
                for webhook in webhooks:
                    if webhook.user == bot.user and webhook.name == 'Cross_Server_Chat_Webhook':
                        webhook_exists = True
                        break
                if not webhook_exists:
                    webhook = await (bot.get_channel(int(channel))).create_webhook(name='Cross_Server_Chat_Webhook')
                message_files = []
                message_embeds = []
                if len(message.attachments) > 0:
                    for attach in message.attachments:
                        file = await attach.to_file()
                        message_files.append(file)
                if len(message.embeds) > 0 and 'https://' not in message.content and 'http://' not in message.content:
                    message_embeds = message.embeds
                await webhook.send(message.content,
                                   username=f"{message.author.name} ({message.author.guild.name})",
                                   avatar_url=message.author.avatar, files=message_files, embeds=message_embeds)
            except:
                if not bot.get_channel(int(channel)):
                    for o in db.query(LINKED).all():
                        if channel == o.CHANNEL_ID:
                            db.delete(o)
                            db.commit()
                        if channel in o.LINKED_CHANNELS_ID:
                            channels = o.LINKED_CHANNELS_ID.split(":")
                            channels.remove(channel)
                            o.LINKED_CHANNELS_ID = ":".join(channels)
                            if not o.LINKED_CHANNELS_ID:
                                db.delete(o)
                                db.commit()
                            else:
                                db.add(o)
                                db.commit()
                    for o in db.query(GUILDS).all():
                        if channel in o.LINKED_CHANNELS_ID:
                            channels = o.LINKED_CHANNELS_ID.split(":")
                            channels.remove(channel)
                            o.LINKED_CHANNELS_ID = ":".join(channels)
                            if not o.LINKED_CHANNELS_ID:
                                o.LINKED_CHANNELS_ID = None
                            db.add(o)
                            db.commit()


    # if message.content.split(" ")[0] == '!post':
    #     for role_id in WHO_CAN_USE_BOT:
    #         role = message.guild.get_role(role_id)
    #         if role in message.author.roles:
    #             await message.delete()
    #             if '$' in message.content:
    #                 text = message.content[6:].split('$')[2]
    #                 embed = discord.Embed(title=f"{message.content[6:].split('$')[1]}", description=f"\n\n{text}",
    #                                       color=0x00BF32)
    #                 if len(message.attachments) > 0:
    #                     attachment = message.attachments[0]
    #                     if attachment.filename.endswith(".jpg") or attachment.filename.endswith(
    #                             ".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(
    #                             ".webp") or attachment.filename.endswith(".gif"):
    #                         image = attachment.url
    #                     elif "https://images-ext-1.discordapp.net" in message.content or "https://tenor.com/view/" in message.content:
    #                         image = message.content
    #                     embed.set_image(url=image)
    #                 embed.set_footer(text=f'Автор поста: {message.author.name}')
    #                 await message.channel.send(embed=embed)
    #             else:
    #                 text = message.content[6:]
    #                 embed = discord.Embed(description=f"{text}", color=0x00BF32)
    #                 if len(message.attachments) > 0:
    #                     attachment = message.attachments[0]
    #                     if attachment.filename.endswith(".jpg") or attachment.filename.endswith(
    #                             ".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(
    #                             ".webp") or attachment.filename.endswith(".gif"):
    #                         image = attachment.url
    #                     elif "https://images-ext-1.discordapp.net" in message.content or "https://tenor.com/view/" in message.content:
    #                         image = message.content
    #                     embed.set_image(url=image)
    #                 embed.set_footer(text=f'Автор поста: {message.author.name}')
    #                 await message.channel.send(embed=embed)
    #             return
    #     await message.channel.reply("У вас недостаточно прав для использования этой команды.", delete_after=7.0)
    # if message.content.split(" ")[0] == '!say':
    #     for role_id in WHO_CAN_USE_BOT:
    #         role = message.guild.get_role(role_id)
    #         if role in message.author.roles:
    #             await message.delete()
    #             await message.channel.send(message.content[5:])
    #             return
    #     await message.channel.reply("У вас недостаточно прав для использования этой команды.", delete_after=7.0)


@bot.slash_command(name='link_guild', description='Создать общий чат с другим дисокрд сервером')
@discord.ext.commands.has_guild_permissions(administrator=True)
@discord.ext.commands.cooldown(1,  1, type=discord.ext.commands.BucketType.guild)
async def link_guild(ctx,
                      guild_id: Option(str, description="Введите id дискорд сервера: ",  required=True),
                      channel: Option(str, description="Введите id канала, который станет общим чатом: ", required=True)):
    if db.get(LINKED, channel):
        for channel_ in (db.get(LINKED, channel).LINKED_CHANNELS_ID).split(":"):
            if not bot.get_channel(int(channel_)):
                for o in db.query(LINKED).all():
                    if channel_ == o.CHANNEL_ID:
                        db.delete(o)
                        db.commit()
                    if channel_ in o.LINKED_CHANNELS_ID:
                        channels = o.LINKED_CHANNELS_ID.split(":")
                        channels.remove(channel_)
                        o.LINKED_CHANNELS_ID = ":".join(channels)
                        if not o.LINKED_CHANNELS_ID:
                            db.delete(o)
                            db.commit()
                        else:
                            db.add(o)
                            db.commit()
                for o in db.query(GUILDS).all():
                    if channel_ in o.LINKED_CHANNELS_ID:
                        channels = o.LINKED_CHANNELS_ID.split(":")
                        channels.remove(channel_)
                        o.LINKED_CHANNELS_ID = ":".join(channels)
                        if not o.LINKED_CHANNELS_ID:
                            o.LINKED_CHANNELS_ID = None
                        db.add(o)
                        db.commit()
    if db.get(LINKED, channel) and guild_id in \
            [str((bot.get_channel(int(channel_))).guild.id) for channel_ in \
            (db.get(LINKED, channel).LINKED_CHANNELS_ID).split(":")]:
        embed = discord.Embed(title="` ОШИБКА! `",
                              description=f"**Канал уже слинкован с ` {bot.get_guild(int(guild_id))} `**",
                              color=0xff0000)
        await ctx.respond(embed=embed)
        return
    if guild_id in [str(guild.id) for guild in bot.guilds] and \
            channel in [str(channel_.id) for channel_ in bot.get_all_channels()]:
        guild_object = db.get(GUILDS, str(ctx.guild.id))
        guild_object.LINK_WAITING_CHANNEL_ID = channel
        db.add(guild_object)
        db.commit()
        guilds = ""
        if (db.get(LINKED, channel)):
            guilds = "` " + "` \n `".join([(bot.get_channel(int(channel_))).guild.name for channel_ in \
                                           ((db.get(LINKED, channel)).LINKED_CHANNELS_ID).split(':') if \
                                           (bot.get_channel(int(channel_)))]) + " `"
        other_guild = bot.get_guild(int(guild_id))
        if other_guild.system_channel:
            other_guild_channel = other_guild.system_channel
        else:
            other_guild_channel = bot.get_channel(random.choice([channel.id for channel in other_guild.text_channels]))
        other_guild_embed = discord.Embed(title="` ПРИГЛАШЕНИЕ ПРИСОЕДИНИТЬСЯ К ОБЩЕМУ КАНАЛУ `",
                                          description=f"**Здравствуйте, уважаемый {other_guild.owner.mention}!\n\n"
                                                      f"Дискорд сервер **` {ctx.guild.name} `**\n"
                                                      f"приглашает вас присоединится к общему каналу.**\n"
                                                      f"` Сервера-участники: `\n\n"
                                                      f"` {ctx.guild.name} `\n"
                                                      f"{guilds}",
                                          color=0x00BF32)
        other_guild_embed.set_footer(text=f'id приглащающего сервера: |{ctx.guild.id}|')
        await other_guild_channel.send(embed=other_guild_embed,
                                       view=link_channel_request())
        embed = discord.Embed(title="` ЗАПРОС ОТПРАВЛЕН! `",
                              description=f"**Приглашение на присоединение \n"
                                          f"сервера **` {other_guild.name} `** к \n"
                                          f"общему каналу <#{channel}>\n"
                                          f"отправлено успешно!\n"
                                          f"(Отправлено в канал <#{other_guild_channel.id}>)\n\n"
                                          f"__Пожалуйста, ожидайте принятия приглашения.__**",
                              color=0x00BF32)
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="` ОШИБКА! `",
                              description=f"**Некорректный дискорд сервер или\n"
                                          f"указан несуществующий канал.\n\n"
                                          f"Если вы уверены, что данные введены\n"
                                          f"правильно, пожалуйста, убедитесь в том,\n"
                                          f"что {bot.user.mention} установлен\n"
                                          f" на обоих дискорд серверах.**",
                              color=0xff0000)
        await ctx.respond(embed=embed)


@bot.slash_command(name='link_telegram', description='Создать общий чат с телеграм-группой (Подробнее: /help link_telegram)')
@discord.ext.commands.has_guild_permissions(administrator=True)
@discord.ext.commands.cooldown(1,  1, type=discord.ext.commands.BucketType.guild)
async def link_telegram(ctx,
                      group_id: Option(str, description="Введите id телеграм-группы: ",  required=True),
                      channel_id: Option(str, description="Введите id канала, который станет общим чатом: ", required=True)):
    error_message_embed = discord.Embed(title='**` ОШИБКА `**',
                                        description="Проверьте правильность введённых данных,\n"
                                                    "а так же убедитесь в том, что [**__RotexBot__**](https://t.me/R7Bot_bot):\n"
                                                    "установлен в целевой телеграм-группе!\n\n"
                                                    "__Подробнее в:__ `/help link_telegram `",
                                        color=0xff0000)
    if not db.get(GROUPS, group_id) or not bot.get_channel(int(channel_id)):
        await ctx.respond(embed=error_message_embed)
    if db.get(GROUPS, group_id).LINKED_CHANNEL_ID:
        embed = discord.Embed(title='**` ОШИБКА `**',
                              description='Данная телеграм группа уже связана с дискород сервером!\n'
                                          'Выберите другой телеграм-чат, или попросите администратора\n'
                                          'телеграм-группы отвязать её с помощью /undiscord команды.',
                              color=0xff0000)
        await ctx.respond(embed=embed)
        return
    if db.get(GUILDS, str(ctx.guild.id)).TG_LINKED_CHANNELS_ID and \
            channel_id in db.get(GUILDS, str(ctx.guild.id)).TG_LINKED_CHANNELS_ID.split(':'):
        embed = discord.Embed(title='**` ОШИБКА `**',
                              description='Выбранный дискорд канал уже связан с телеграм группой!\n'
                                      'Выберите другой канал, или отвяжите телеграм-группу\n'
                                      'от канала с помощью команды `/unlink_telegram`!',
                              color=0xff0000)
        await ctx.respond(embed=embed)
        return
    else:
        try:
            tg_message = f"⸨ СИСТЕМНОЕ СООБЩЕНИЕ ⸩\n\n" \
                         f"Дискорд сервер «{ctx.guild.name}»\n" \
                         f"приглашает ваш Telegram канал создать общий чат!\n" \
                         f"Чтобы завершить создание общего канала, введите:\n\n" \
                         f"/discord {ctx.guild.id}\n"
            url = f"https://api.telegram.org/bot{TG_TOKEN}"
            method = url + "/sendMessage"
            r = requests.post(method, data={
                "chat_id": int(group_id),
                "text": tg_message
            })
            if r.status_code != 200:
                raise Exception("ЕГГОР! Код НЕ 200!")

            guild_object = db.get(GUILDS, str(ctx.guild.id))
            guild_object.TG_LINK_WATING_GROUP_ID = group_id
            guild_object.TG_LINK_WATING_CHANNEL_ID = channel_id
            db.add(guild_object)
            db.commit()

            webhooks = await (bot.get_channel(int(channel_id))).webhooks()
            for webhook in webhooks:
                if webhook.user == bot.user and webhook.name == 'RotexBot_telegram_connection_webhook':
                    await webhook.delete()
            tg_webhook = await (bot.get_channel(int(channel_id))).create_webhook(name='RotexBot_telegram_connection_webhook')
            db.add(WEBHOOKS(CHANNEL_ID=channel_id, WEBHOOK_URL=tg_webhook.url))
            db.commit()

            embed = discord.Embed(title="**` ЗАПРОС ОТПРАВЛЕН УСПЕШНО! `**",
                                  description=f"**Чтобы завершить установку соединения, пожалуйста,\n"
                                              f"введите в телеграм-группе следующую команду:**\n\n"
                                              f"`/discord {ctx.guild.id}`",
                                  colour=0x00BF32)
            await ctx.respond(embed=embed)
        except Exception as e:
            print(e)


@bot.slash_command(name='test', description='Да, это тест.')
async def test(ctx):
    await ctx.respond('Да, это тест!')


@bot.slash_command(name='help', description='обзор фукнционала бота')
async def help(ctx):
    embed_text = discord.Embed(title=f"` Список доступных команд `", description=COMMAND_LIST, color=0x00BF32)
    await ctx.respond(embed=embed_text)


@bot.command()
async def hey(ctx):
    await ctx.reply(f"I am alive!", mention_author=False)



# @bot.command()
# @discord.ext.commands.has_guild_permissions(moderate_members=True)
# async def clear(ctx, limit):
#     flag = False
#     for role_id in WHO_CAN_USE_BOT:
#         role = ctx.guild.get_role(role_id)
#         if role in ctx.author.roles:
#             flag = True
#     if not flag:
#         await ctx.reply("У вас недостаточно прав для использования этой команды!", delete_after=7.0)
#         return
#     # messages = [message async for message in channel.history(limit=123)]
#     limit = int(limit) + 1
#     embed = discord.Embed(title=f"Очищено `{limit - 1}` сообщений в <#{ctx.channel.id}>:", color=0xff0000,
#                           timestamp=datetime.datetime.utcnow())
#     channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
#     embed.set_footer(text=f'Модератор: {ctx.author}')
#     await ctx.channel.purge(limit=limit)
#     await ctx.send(embed=embed, delete_after=10.0)
#     await channel.send(embed=embed)


# @bot.command()
# @discord.ext.commands.has_guild_permissions(moderate_members=True)
# async def mute(ctx, member: discord.Member, time, *reason):
#     flag = False
#     for role_id in WHO_CAN_USE_BOT:
#         role = ctx.guild.get_role(role_id)
#         if role in ctx.author.roles:
#             flag = True
#     if not flag:
#         await ctx.reply("У вас недостаточно прав для использования этой команды!", delete_after=7.0)
#         return
#     if not reason:
#         reason = ['не указана.']
#     if time[-1] not in 'mhd':
#         time = f'{time}h'
#     if time[-1] == 'm':
#         if time[-2] in '1':
#             full_time = f'{time[:-1]} минуту'
#         elif time[-2] in '234':
#             full_time = f'{time[:-1]} минуты'
#         elif time[-2] in '567890':
#             full_time = f'{time[:-1]} минут'
#         time = int(time[0:-1])
#         until = (datetime.datetime.utcnow() + datetime.timedelta(minutes=time))
#     elif time[-1] == 'h':
#         if time[-2] in '1':
#             full_time = f'{time[:-1]} час'
#         elif time[-2] in '234':
#             full_time = f'{time[:-1]} часа'
#         elif time[-2] in '567890':
#             full_time = f'{time[:-1]} часов'
#         time = int(time[0:-1])
#         until = (datetime.datetime.utcnow() + datetime.timedelta(hours=time))
#     elif time[-1] == 'd':
#         if int(time[:-1]) > 28:
#             await ctx.reply('Из за ограничений дискорда невозможно выдать мут более, чем на 28 дней!', delete_after=5.0)
#             await asyncio.sleep(5)
#             await ctx.message.delete()
#         if time[-2] in '1':
#             full_time = f'{time[:-1]} день'
#         elif time[-2] in '234':
#             full_time = f'{time[:-1]} дня'
#         elif time[-2] in '567890':
#             full_time = f'{time[:-1]} дней'
#         time = int(time[0:-1])
#         until = (datetime.datetime.utcnow() + datetime.timedelta(days=time))
#
#     await member.timeout(until, reason=None)
#     await ctx.message.delete()
#     channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
#     embed = discord.Embed(title=f"Хоба!",
#                           description=f"{member.mention} был выдан мут на {full_time}. \n`Причина:` {' '.join(reason)}",
#                           color=0xff0000)
#     embed.set_footer(text=f'Участника замутил {ctx.author}')
#     await channel.send(embed=embed)
#     await ctx.send(embed=embed, delete_after=60.0)
#
#
# @bot.command()
# @discord.ext.commands.has_guild_permissions(moderate_members=True)
# async def unmute(ctx, member: discord.Member):
#     flag = False
#     for role_id in WHO_CAN_USE_BOT:
#         role = ctx.guild.get_role(role_id)
#         if role in ctx.author.roles:
#             flag = True
#     if not flag:
#         await ctx.send("У вас недостаточно прав для использования этой команды!")
#         return
#     time = 0
#     until = (datetime.datetime.utcnow() + datetime.timedelta(minutes=time))
#     await member.timeout(until, reason=None)
#     await ctx.message.delete()
#     channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
#     embed = discord.Embed(title=f"Ура!", description=f"С участника {member.mention} был снят мут.", color=0x00BF32)
#     embed.set_footer(text=f'Участника размутил {ctx.author}')
#     await channel.send(embed=embed)
#     await ctx.send(embed=embed, delete_after=60.0)


@bot.slash_command(name='id', description='Узнать id дискорд сервера, а также id его каналов')
async def id(ctx):
    # def split_list(ids_list):
    #     splited_list = []
    #     for sublist in ids_list:
    #         splited_list.append(sublist[:(len(sublist) // 2)])
    #         splited_list.append(sublist[(len(sublist) // 2):])
    #     return splited_list

    ids_list = []
    for category in ctx.guild.categories:
        category_list = []
        category_list.append(f'**```{category.name}```**')
        category_list.append('`=============================================================`')
        for channel in category.text_channels:
            if ctx.author in channel.members:
                category_list.append(f'{channel.mention}  —  **`{channel.id}`**')
        if len(category_list) > 2:
            ids_list.append(category_list)



    # list_of_id = []
    # for channel in ctx.guild.text_channels:
    #     list_of_id.append(f'{channel.mention}  —  **`{channel.id}`**')
    # ids_list = [list_of_id]
    # if len("\n".join(list_of_id)) >= 1024:
    #     while len("\n".join(ids_list[0])) >= 1024:
    #         ids_list = split_list(ids_list)
    main_embed = discord.Embed(title='**` СПИСОК ID `**',
                          description=f'`=============================================================`\n'
                                      f'**```ansi\n[2;34m ID сервера {ctx.guild.name}: [0m\n```**\n'
                                      f'`{ctx.guild.id}`\n'
                                      f'**```ansi\n[2;34m ID текущего канала: [0m\n```**\n'
                                      f'`{ctx.channel.id}`\n'
                                      f'**```ansi\n[2;34m ID всех текстовых каналов: [0m\n```**',
                          color=0x2b2d31)
    await ctx.respond(embed=main_embed)
    for short_ids_list in ids_list:
        embed = discord.Embed(title=short_ids_list[0],
                              description="\n".join(short_ids_list[1:]),
                              color=0x2b2d31)
        await ctx.send(embed=embed)




@bot.slash_command(name='stats', description='Просмотреть статистику пользователя')
async def stats(ctx, member: Option(discord.Member, description="Выберите пользователя: ",  required=False)):
    if not member:
        member = ctx.author
    if member.raw_status in "dnd,idle,invisible,online":
        status = 'В сети'
    else:
        status = 'Не в сети'
    embed = discord.Embed(title=f"Статистика пользователя", description=f"", color=0x00BF32)
    embed.add_field(name="`Статус:`", value=f"{status}", inline=False)
    embed.add_field(name="`Аккаунт создан:`", value=f"{member.created_at.strftime('%Y.%m.%d - %H:%M')}", inline=False)
    embed.add_field(name="`Присоединился к серверу`", value=f"{member.joined_at.strftime('%Y.%m.%d - %H:%M')}",
                    inline=False)
    embed.set_author(name=f"{member}", icon_url=member.avatar)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=f'Статистика предоставлена по запросу {ctx.author}')
    await ctx.respond(embed=embed)


@bot.slash_command(name='weather', description='Узнать прогноз погоды в выбранном городе')
async def weather(ctx,
                  place: Option(str, description="Введите название города: ",  required=True)):
    appid = 'ef526c997e6a909c2a978311053fe37e'
    try:
        limit = 5
        res = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={place}&limit={limit}&appid={appid}")
        data = res.json()
        lat = data[0]['lat']
        lon = data[0]['lon']
        res = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=ru&appid={appid}")
        data = res.json()

        weather_forecast = []
        wind_deg_list = []
        temp_list = []
        wind_speed_list = []
        humidity_list = []
        weather_list = []
        date = data['list'][0]['dt_txt'].split()[0]
        for part in data['list']:
            if part['dt_txt'].split()[0] != date:
                wind_deg = int(mean(wind_deg_list))
                min_temp = round(min(temp_list))
                max_temp = round(max(temp_list))
                min_wind = round(min(wind_speed_list))
                max_wind = round(max(wind_speed_list))
                humidity = round(mean(humidity_list))
                weather = mode(weather_list)
                if wind_deg in range(338, 360) or wind_deg in range(0, 23):
                    wind = '⬆'
                elif wind_deg in range(23, 68):
                    wind = '↗'
                elif wind_deg in range(68, 113):
                    wind = '➡'
                elif wind_deg in range(113, 158):
                    wind = '↘'
                elif wind_deg in range(158, 203):
                    wind = '⬇'
                elif wind_deg in range(203, 248):
                    wind = '↙'
                elif wind_deg in range(248, 293):
                    wind = '⬅'
                elif wind_deg in range(293, 338):
                    wind = '↖'

                mounths = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентбря', 'октября', 'ноября', 'декабря']

                date = f"""```ansi\n[2;34m---===≡≡╠ {int(date.split("-")[2])} {mounths[int(date.split("-")[1]) - 1]} ╣≡≡===---[0m\n```"""

                weather_forecast.append(f'{date}  `Погода:` **{weather}**\n  `Температура:` **от {min_temp} до {max_temp}°C**\n  `Ветер:` **`〔{wind}〕`** **от {min_wind} до {max_wind}м/с**\n  `Влажность:` **{humidity}%**')

                wind_deg_list = []
                temp_list = []
                wind_speed_list = []
                humidity_list = []
                weather_list = []
                date = part['dt_txt'].split()[0]

            temp = part['main']['temp']
            humidity = part['main']['humidity']
            description = part['weather'][0]['description']
            wind_speed = part['wind']['speed']
            wind_deg = int(part['wind']['deg'])

            temp_list.append(temp)
            humidity_list.append(humidity)
            weather_list.append(description)
            wind_speed_list.append(wind_speed)
            wind_deg_list.append(wind_deg)

        title = f"``` {place} ```\n` {round(lat, 6)} {round(lon, 6)} `\n"
        text = '\n'.join(weather_forecast)
        embed = discord.Embed(title=title, description=text, color=0x2b2d31)
        await ctx.respond(embed=embed)
        # await ctx.reply((f"```{city}\n{round(lat, 4)} {round(lon, 4)}\nпрогноз погоды на 5 дней:\n\n```" + '\n\n'.join(weather_forecast)))
    except Exception as e:
        print(e)
        embed = discord.Embed(title='` ОШИБКА `', description='**Пожалуйста, введите корректное \nназвание города или страны**', color=0xff0000)
        await ctx.respond(embed=embed, delete_after=7.0)



class link_channel_request(discord.ui.View):
    def __init__(self, *, timeout=1000000000000000000000):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Присоединиться", style=discord.ButtonStyle.green)
    async def green_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = link_channel_request_modal(title="Присоединение к общему каналу")
        await interaction.response.send_modal(modal)


class link_channel_request_modal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Канал, который станет общим чатом",
                                           placeholder='Введите id канала'))

    async def callback(self, interaction: discord.Interaction):
        if ((self.children[0].value).strip()).isdigit() and \
                bot.get_channel(int(self.children[0].value.replace(" ", ""))) in interaction.guild.channels and \
                bot.get_channel(int(self.children[0].value.replace(" ", ""))) not in interaction.guild.voice_channels:
            channel = bot.get_channel(int(self.children[0].value.replace(" ", "")))
            embed = discord.Embed(title="` ПОДТВЕРДИТЕ ДЕЙСТВИЕ `",
                                  description=f"**Вы уверены, что хотите сделать канал\n\n"
                                              f"<#{channel.id}> общим чатом?**",
                                  color=0xff0000)
            embed.set_footer(text=f'id выбранного канала: |{channel.id}|\n{interaction.message.embeds[0].footer.text}')
            await interaction.response.send_message(embed=embed, view=is_link_channel_id_correct(), ephemeral=True, delete_after=30.0)
        else:
            embed = discord.Embed(title="` НЕКОРРЕКТНОЕ ЗНАЧЕНИЕ Id КАНАЛА `",
                                  description=f"**Пожалуйста, проверьте правильность введённых даныых.**\n\n"
                                              f"`Пример id канала:`   1068566917461327912",
                                  color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10.0)


class is_link_channel_id_correct(discord.ui.View):
    def __init__(self, *, timeout=1000000000000000000000):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Так точно! ✔", style=discord.ButtonStyle.green)
    async def green_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        another_guild_id = int(interaction.message.embeds[0].footer.text.split('|')[3])
        another_guild_object = db.get(GUILDS, str(another_guild_id))
        guild_object = db.get(GUILDS, str(interaction.guild.id))
        channel_id = interaction.message.embeds[0].footer.text.split('|')[1]

        if not db.get(GUILDS, str(another_guild_id)).LINK_WAITING_CHANNEL_ID:
            embed = discord.Embed(title="` ОШИБКА `",
                                  description=f"**Вы уже приняли запрос от ** ` {bot.get_guild(another_guild_id).name} `\n"
                                              f"**или время действия запроса истекло!**",
                                  color=0xff0000)
            await interaction.response.edit_message(embed=embed, view=None, delete_after=7.0)
            return


        # if db.get(LINKED, channel_id):
        #     for channel_ in (db.get(LINKED, channel_id).LINKED_CHANNELS_ID).split(":"):
        #         if bot.get_channel(int(channel_)) and bot.get_channel(int(channel_)).guild.id == another_guild_id:
        #             embed = discord.Embed(title="` ОШИБКА `",
        #                                   description=f"**Канал уже слинкован с** ` {bot.get_guild(another_guild_id).name} `\n"
        #                                               f"Пожалуйста, выберите другой канал или\n откажитесь от присоединения!",
        #                                   color=0xff0000)
        #             await interaction.response.edit_message(embed=embed, view=None, delete_after=7.0)
        #             return
        if channel_id in [o.CHANNEL_ID for o in db.query(LINKED).all()]:
            embed = discord.Embed(title="` ОШИБКА `",
                                          description=f"**Канал уже слинкован с другой гильдией!\n"
                                                      f"Пожалуйста, выберите другой канал или\n откажитесь от присоединения!**",
                                          color=0xff0000)
            await interaction.response.edit_message(embed=embed, view=None, delete_after=7.0)
            return

        if another_guild_object.LINKED_CHANNELS_ID:
            channels_list = (another_guild_object.LINKED_CHANNELS_ID).split(":")
            if another_guild_object.LINK_WAITING_CHANNEL_ID not in channels_list:
                channels_list.append(another_guild_object.LINK_WAITING_CHANNEL_ID)
            another_guild_object.LINKED_CHANNELS_ID = ":".join(channels_list)
        else:
            another_guild_object.LINKED_CHANNELS_ID = another_guild_object.LINK_WAITING_CHANNEL_ID
        db.add(another_guild_object)
        db.commit()


        if guild_object.LINKED_CHANNELS_ID:
            channels_list = guild_object.LINKED_CHANNELS_ID.split(":")
            if channel_id not in channels_list:
                channels_list.append(channel_id)
            guild_object.LINKED_CHANNELS_ID = ":".join(channels_list)
        else:
            guild_object.LINKED_CHANNELS_ID = channel_id
        db.add(guild_object)
        db.commit()


        if channel_id in [o.CHANNEL_ID for o in db.query(LINKED).all()]:
            pass
        else:
            if db.get(LINKED, another_guild_object.LINK_WAITING_CHANNEL_ID) and \
                    db.get(LINKED, another_guild_object.LINK_WAITING_CHANNEL_ID).LINKED_CHANNELS_ID:

                channels_list = db.get(LINKED, another_guild_object.LINK_WAITING_CHANNEL_ID).LINKED_CHANNELS_ID.split(":")
                if another_guild_object.LINK_WAITING_CHANNEL_ID not in channels_list:
                    channels_list.append(another_guild_object.LINK_WAITING_CHANNEL_ID)
                CHANNEL = LINKED(CHANNEL_ID=channel_id,
                             LINKED_CHANNELS_ID=":".join(channels_list))
            else:
                CHANNEL = LINKED(CHANNEL_ID=channel_id,
                             LINKED_CHANNELS_ID=another_guild_object.LINK_WAITING_CHANNEL_ID)
            db.add(CHANNEL)
            db.commit()


        if another_guild_object.LINK_WAITING_CHANNEL_ID in [o.CHANNEL_ID for o in db.query(LINKED).all()]:
            for channel_ in db.get(LINKED, another_guild_object.LINK_WAITING_CHANNEL_ID).LINKED_CHANNELS_ID.split(":"):
                o = db.get(LINKED, channel_)
                channels_list = o.LINKED_CHANNELS_ID.split(":")
                if channel_id not in channels_list:
                    channels_list.append(channel_id)
                o.LINKED_CHANNELS_ID = ":".join(channels_list)
                db.add(o)
                db.commit()
            o = db.get(LINKED, another_guild_object.LINK_WAITING_CHANNEL_ID)
            channels_list = o.LINKED_CHANNELS_ID.split(":")
            if channel_id not in channels_list:
                channels_list.append(channel_id)
            o.LINKED_CHANNELS_ID = ":".join(channels_list)
            db.add(o)
            db.commit()
        else:
            CHANNEL = LINKED(CHANNEL_ID=another_guild_object.LINK_WAITING_CHANNEL_ID,
                             LINKED_CHANNELS_ID=channel_id)
            db.add(CHANNEL)
            db.commit()


        db.add(another_guild_object)
        db.add(guild_object)
        another_guild_object.LINK_WAITING_CHANNEL_ID = None
        guild_object.LINK_WAITING_CHANNEL_ID = None
        db.commit()

        embed = discord.Embed(title="` УСПЕШНО! ✔ `",
                              description=f"**Присоединение к общему чату завершено!\n**",
                              color=0x00BF32)
        embed.set_footer(text=f'{interaction.message.embeds[0].footer.text}')
        await interaction.response.edit_message(embed=embed, view=None, delete_after=15.0)


    @discord.ui.button(label="Закрыть ❌", style=discord.ButtonStyle.green)
    async def red_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(title="` ЗАКРЫТИЕ `",
                              color=0xff0000)
        await interaction.response.edit_message(embed=embed, view=None, delete_after=0.0)



class Buttons_DELETE(discord.ui.View):
    def __init__(self, *, timeout=1000000000000000000000):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="❌ Удалить!", style=discord.ButtonStyle.red)
    async def red_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Автоматическое удаление канала через несколько секунд.')
        await asyncio.sleep(7)
        await interaction.channel.delete()

    @discord.ui.button(label="❎ Отменить!", style=discord.ButtonStyle.green)
    async def green_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()


# @bot.event
# async def on_message_delete(message):
#     try:
#         startswith = message.content.split()[0]
#     except:
#         startswith = None
#     if startswith and startswith in COMMAND_LIST or message.channel.id == AUDIT_LOG_CHANNEL_ID or message.author == bot.user:
#         return
#     embed = discord.Embed(title=f"Сообщение удалено в <#{message.channel.id}>:", description=f"{message.content}",
#                           color=0xff0000, timestamp=datetime.datetime.utcnow())
#     embed.set_author(name=f"{message.author} (автор сообщения)", icon_url=message.author.avatar)
#     channel = bot.get_channel(AUDIT_LOG_CHANNEL_ID)
#     files = None
#     embeds = None
#     if len(message.attachments) > 0:
#         files = []
#         for attach in message.attachments:
#             file = await attach.to_file()
#             files.append(file)
#     if len(message.embeds) > 0:
#         embeds = message.embeds
#     log_message = await channel.send(embed=embed)
#     if embeds or files:
#         log_message_end = await log_message.reply('⬇ `Вложения` ⬇ `удалённого` ⬇ `сообщения` ⬇', embeds=embeds,
#                                                   files=files)
#         await channel.send('⬆ `Вложения` ⬆ `удалённого` ⬆ ` сообщения` ⬆')


@bot.event
async def on_ready():
    global BOT_IS_READY
    activity = discord.Activity(type=discord.ActivityType.custom, name="Тестовая активность")
    await bot.change_presence(activity=activity)

    BOT_IS_READY = True
    print('Discord-bot started successfully!')


@bot.event
async def on_guild_join(guild):
    if not db.get(GUILDS, guild.id):
        GUILD = GUILDS(GUILD_ID=guild.id)
        db.add(GUILD)
        db.commit()
    print('бот стал членом гильдии:  ', guild.id)
    pass


@bot.event
async def on_guild_remove(guild):
    print('бот покинул гильдию:  ', guild.id)
    pass


bot.run(DS_TOKEN)
