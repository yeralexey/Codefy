from main import *


@Client.on_message(filters.private & filters.user(config.admins) & filters.command(
    ['restart', 'reboot', 'kill', 'setindex', 'admin', 'commands']))
async def from_admins(client, message):
    user = await User.get_user(message.chat.id)
    if message.command[0] == 'restart':
        await message.reply(plate("admin_on_restart", user.chosen_language))
        cr.restart()
    if message.command[0] == 'reboot':
        await message.reply(plate("admin_on_reboot", user.chosen_language))
        cr.reboot()
    if message.command[0] == 'kill':
        await message.reply(plate("admin_on_kill", user.chosen_language))
        cr.kill()
    if message.command[0] == 'setindex':
        await Client.send_message(client, message.chat.id, plate("admin_on_setindex", user.chosen_language))

        try:
            answer = await client.listen(message.chat.id, timeout=15)
        except listen.ListenerStopped:
            logger.debug("listener cancelled")
            return
        except listen.ListenerTimeout:
            logger.debug("listener timeout")
            return
        except Exception as err:
            logger.exception(err)
            return

        if not answer.text.isdigit():
            await message.reply(plate("admin_on_setindex_invalid_input", user.chosen_language))
            return
        await User.main_index(value=answer.text)
        await message.reply(plate("admin_on_setindex_changed", user.chosen_language))
    if message.command[0] == 'admin':
        await admin_menu(client, message)
    if message.command[0] == 'commands':
        await message.reply(f'/restart  - {plate("admin_its_restart", user.chosen_language)}'
                            f'/reboot   - {plate("admin_its_reboot", user.chosen_language)}'
                            f'/kill     - {plate("admin_its_kill", user.chosen_language)}'
                            f'/setindex  - {plate("admin_its_setindex", user.chosen_language)}'
                            f'/admin    -  {plate("admin_its_admin", user.chosen_language)}'
                            f'/commands - {plate("admin_its_commands", user.chosen_language)}')


async def admin_menu(client, message):
    user = await User.get_user(message.chat.id)
    keyboard = ikb([
        [(plate("admin_menu_url", user.chosen_language),
          f'https://docs.google.com/spreadsheets/d/{config.main_sheet}/', 'url')],
        [(plate("admin_menu_log", user.chosen_language), 'admin_getlog')],
        [(plate("admin_menu_csv", user.chosen_language), 'admin_getcsvbase')],
        [(plate("admin_menu_db", user.chosen_language), 'admin_getdbbase')],
        [(plate("admin_menu_restore_db", user.chosen_language), 'admin_restoredb')],
        [(plate("admin_menu_send_all", user.chosen_language), 'admin_messageall')],
        [(plate("admin_menu_send_list", user.chosen_language), 'admin_messagelist')]
    ])
    await message.reply(plate("admin_menu", user.chosen_language), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(pattern='admin'))
async def admin_acts(client, call):
    user = await User.get_user(call.message.chat.id)
    chat_id = call.message.chat.id

    if call.data == 'admin_getlog':
        await Client.send_document(client, chat_id, config.main_log)

    if call.data == 'admin_getcsvbase':
        await Client.send_message(client, chat_id, plate("admin_collect_csv_response", user.chosen_language))
        database = []
        all_users_list = await User.get_users()
        all_attributes_list = await User.get_attribute_list()
        all_attributes_table_names = ";".join(all_attributes_list)
        for item in all_users_list:
            all_attributes_f_str = f""
            for attr in all_attributes_list:
                all_attributes_f_str = all_attributes_f_str + f"{await User(item).get_attribute(attr, setit=False)};"
            database.append(all_attributes_f_str)
        with open(config.csv_file, 'w', encoding='utf-8') as file:
            file.write(all_attributes_table_names + '\n')
            file.write("\n".join(database))
        await Client.send_document(client, chat_id, config.csv_file)

    if call.data == 'admin_getdbbase':
        await Client.send_document(client, chat_id, config.db_file)

    if call.data == 'admin_restoredb':
        await Client.send_message(client, chat_id, plate("admin_restore_db_response", user.chosen_language))

        try:
            answer = await call.message.chat.listen(timeout=30)
        except listen.ListenerStopped:
            logger.debug("listener cancelled")
            return
        except listen.ListenerTimeout:
            logger.debug("listener timeout")
            return
        except Exception as err:
            logger.exception(err)
            return

        if answer.document.file_name != str(config.db_file).split('/')[-1]:
            await Client.send_message(client, chat_id, plate("admin_restore_db_fail", user.chosen_language))
            return
        await answer.download(config.db_file)
        await Client.send_message(client, chat_id, plate("admin_restore_db_confirm", user.chosen_language))

    if call.data == 'admin_messageall':
        await Client.send_message(client, chat_id, plate("admin_send_all_confirmation_request", user.chosen_language))

        try:
            answer = await call.message.chat.listen(timeout=30)
        except listen.ListenerStopped:
            logger.debug("listener cancelled")
            return
        except listen.ListenerTimeout:
            logger.debug("listener timeout")
            return
        except Exception as err:
            logger.exception(err)
            return

        if answer.text == "active":
            mail_list = await User.get_users(attribute="is_active", checkvalue=True, value=True)
            await start_mailing(client, mail_list, "to_all", message=call.message)
        elif answer.text == "include blocked":
            mail_list = await User.get_users()
            await start_mailing(client, mail_list, "to_all", message=call.message)
        else:
            await Client.send_message(client, chat_id, plate("admin_send_all_abort", user.chosen_language))

    if call.data == 'admin_messagelist':
        await Client.send_message(client, chat_id, plate("admin_send_list_file_request", user.chosen_language))

        try:
            answer = await call.message.chat.listen(timeout=60)
        except listen.ListenerStopped:
            logger.debug("listener cancelled")
            return
        except listen.ListenerTimeout:
            logger.debug("listener timeout")
            return
        except Exception as err:
            logger.exception(err)
            return

        if str(answer.document.file_name).split('.')[1] != "txt":
            await Client.send_message(client, chat_id, plate("admin_send_list_abort", user.chosen_language))
        else:
            file = await answer.download(in_memory=True)
            mail_list = bytes(file.getbuffer()).decode("utf-8").split("\n")
            await start_mailing(client, mail_list, "by_list", message=call.message)


async def start_mailing(client, mail_list, mail_type, message):
    message = message
    chat_id = message.chat.id
    user = await User.get_user(chat_id)
    await Client.send_message(client, chat_id, plate("admin_send_await_repost", user.chosen_language))

    try:
        mail = await message.chat.listen(timeout=60)
    except listen.ListenerStopped:
        logger.debug("listener cancelled")
        return
    except listen.ListenerTimeout:
        logger.debug("listener timeout")
        return
    except Exception as err:
        logger.exception(err)
        return

    await Client.send_message(client, chat_id, plate("admin_send_started", user.chosen_language))
    try:
        log_file_name = f"{config.mail_logs}{mail_type}{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}.csv"
        with open(log_file_name, "w", encoding="utf-8") as file:
            if mail.caption:
                description = mail.caption
            elif mail.text:
                description = mail.text
            else:
                description = "no description"
            file.write(
                f"date: {str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}. \nby: {chat_id}, "
                f"\n\nmessage: {mail.id}\n\n"
                f"description: {description[:50]}...\n\n________________\n\n")
        for mail_id in mail_list:
            when = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if len(mail_id) < 3:
                continue
            try:
                if mail.media_group_id:
                    await Client.copy_media_group(client, int(mail_id), "self", mail.id, captions=mail.caption.html)
                else:
                    await mail.copy(int(mail_id))
                res = f"{mail_id};{when.split('.')[0]};ok"
            except Exception as err:
                logger.exception(err)
                res = f"{mail_id};{when.split('.')[0]};fail"
                await User(mail_id).set_attribute(attribute="is_active", value=False)
            with open(log_file_name, "a", encoding="utf-8") as file:
                file.write(f"\n{res}")
            await asyncio.sleep(1)
        await Client.send_message(client, chat_id, plate("admin_send_success", user.chosen_language))
        await Client.send_document(client, chat_id, log_file_name)
    except Exception as err:
        logger.exception(err)
        await Client.send_message(client, chat_id, plate("admin_send_fail", user.chosen_language))
        await Client.send_message(client, config.admins[0], plate("admin_send_admin_fail", user.chosen_language))
