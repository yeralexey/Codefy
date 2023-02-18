from main import *


@Client.on_message(filters.user(config.admins) & filters.private & filters.command(
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
        await user.set_attribute("current_step", "adminjob_set_index")
        await asyncio.sleep(15)
        await user.set_attribute("current_step", None)
    if message.command[0] == 'admin':
        await admin_menu(client, message)
    if message.command[0] == 'commands':
        await message.reply(f'/restart  - {plate("admin_its_restart", user.chosen_language)}'
                            f'/reboot   - {plate("admin_its_reboot", user.chosen_language)}'
                            f'/kill     - {plate("admin_its_kill", user.chosen_language)}'
                            f'/setindex  - {plate("admin_its_setindex", user.chosen_language)}'
                            f'/admin    -  {plate("admin_its_admin", user.chosen_language)}'
                            f'/commands - {plate("admin_its_commands", user.chosen_language)}')


async def admin_menu(_, message):
    user = await User.get_user(message.chat.id)
    markup = keyboard([
        [(plate("admin_menu_url", user.chosen_language),
          f'https://docs.google.com/spreadsheets/d/{config.main_sheet}/', 'url')],
        [(plate("admin_menu_log", user.chosen_language), 'admin_getlog')],
        [(plate("admin_menu_csv", user.chosen_language), 'admin_getcsvbase')],
        [(plate("admin_menu_db", user.chosen_language), 'admin_getdbbase')],
        [(plate("admin_menu_restore_db", user.chosen_language), 'admin_restoredb')],
        [(plate("admin_menu_send_all", user.chosen_language), 'admin_messageall')],
        [(plate("admin_menu_send_list", user.chosen_language), 'admin_messagelist')]
    ])
    await message.reply(plate("admin_menu", user.chosen_language), reply_markup=markup)


@Client.on_callback_query(filters.user(config.admins) & filters.regex(pattern='admin'))
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
        await user.set_attribute("current_step", "adminjob_restore_db_await_file")
        await asyncio.sleep(30)
        await user.set_attribute("current_step", None)


    if call.data == 'admin_messageall':
        await Client.send_message(client, chat_id, plate("admin_send_all_confirmation_request", user.chosen_language))
        await user.set_attribute("current_step", "adminjob_send_to_all")
        await asyncio.sleep(15)
        await user.set_attribute("current_step", None)
        return


    if call.data == 'admin_messagelist':
        await Client.send_message(client, chat_id, plate("admin_send_list_file_request", user.chosen_language))
        await user.set_attribute("current_step", "adminjob_send_by_list")
        await asyncio.sleep(60)
        await user.set_attribute("current_step", None)
        return


async def start_mailing(client, mail_list, mail_type, message):
    message = message
    chat_id = message.chat.id
    user = await User.get_user(chat_id)
    await Client.send_message(client, chat_id, plate("admin_send_await_repost", user.chosen_language))
    await user.set_attribute("current_step", "start_mailing")
    await user.set_attribute("maildata", (mail_type, mail_list))
    await asyncio.sleep(60)
    await user.set_attribute("current_step", None)
    await user.set_attribute("maildata", None)


@Client.on_message(filters.user(config.admins) & filters.private)
async def continue_mailing_(client, message):
    user = await User.get_user(message.chat.id)
    read_step = await user.get_attribute("current_step")
    if not read_step or read_step != "start_mailing":
        message.continue_propagation()
        return
    mailingdata  = await user.get_user("maildata")
    mail_list = mailingdata[0]
    mail_type = mailingdata[1]
    await user.set_attribute("current_step", None)
    await user.set_attribute("maildata", None)

    await Client.send_message(client, message.chat.id, plate("admin_send_started", user.chosen_language))
    try:
        log_file_name = f"{config.mail_logs}{mail_type}{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}.csv"
        with open(log_file_name, "w", encoding="utf-8") as file:
            if message.caption:
                description = message.caption
            elif message.text:
                description = message.text
            else:
                description = "no description"
            file.write(
                f"date: {str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}. \nby: {message.chat.id}, "
                f"\n\nmessage: {message.id}\n\n"
                f"description: {description[:50]}...\n\n________________\n\n")
        for mail_id in mail_list:
            when = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if len(mail_id) < 3:
                continue
            try:
                if message.media_group_id:
                    await Client.copy_media_group(client, int(mail_id), "self", message.id,
                                                  captions=message.caption.html)
                else:
                    await message.copy(int(mail_id))
                res = f"{mail_id};{when.split('.')[0]};ok"
            except Exception as err:
                logger.exception(err)
                res = f"{mail_id};{when.split('.')[0]};fail"
                await User(mail_id).set_attribute(attribute="is_active", value=False)
            with open(log_file_name, "a", encoding="utf-8") as file:
                file.write(f"\n{res}")
            await asyncio.sleep(1)
        await Client.send_message(client, message.chat.id, plate("admin_send_success", user.chosen_language))
        await Client.send_document(client, message.chat.id, log_file_name)
    except Exception as err:
        logger.exception(err)
        await Client.send_message(client, message.chat.id, plate("admin_send_fail", user.chosen_language))
        await Client.send_message(client, config.admins[0], plate("admin_send_admin_fail", user.chosen_language))


@Client.on_message(filters.private)
async def on_admins_message(client, message):
    user = await User.get_user(message.chat.id)
    read_step = await user.get_attribute("current_step")
    if not read_step or "adminjob" not in read_step:
        await user.set_attribute("current_step", None)
        message.continue_propagation()
        return
    if read_step == "adminjob_restore_db_await_file":
        if message.document.file_name != str(config.db_file).split('/')[-1]:
            await Client.send_message(client, message.chat.id, plate("admin_restore_db_fail", user.chosen_language))
            return
        await message.download(config.db_file)
        await Client.send_message(client, message.chat.id, plate("admin_restore_db_confirm", user.chosen_language))
    if read_step == "adminjob_send_to_all":
        if message.text == "active":
            mail_list = await User.get_users(attribute="is_active", checkvalue=True, value=True)
            await start_mailing(client, mail_list, "to_all", message=message)
        elif message.text == "include blocked":
            mail_list = await User.get_users()
            await start_mailing(client, mail_list, "to_all", message=message)
        else:
            await Client.send_message(client, message.chat.id, plate("admin_send_all_abort", user.chosen_language))

    if read_step == "adminjob_send_by_list":
        if str(message.document.file_name).split('.')[1] != "txt":
            await Client.send_message(client, message.chat.id, plate("admin_send_list_abort", user.chosen_language))
        else:
            file = await message.download(in_memory=True)
            mail_list = bytes(file.getbuffer()).decode("utf-8").split("\n")
            await start_mailing(client, mail_list, "by_list", message=message)

    if read_step == 'adminjob_set_index':
        if not message.text.isdigit():
            await message.reply(plate("admin_on_setindex_invalid_input", user.chosen_language))
            return
        await User.main_index(value=int(message.text))
        await message.reply(plate("admin_on_setindex_changed", user.chosen_language))
