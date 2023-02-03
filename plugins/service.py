from main import *


@Client.on_callback_query(filters.regex(pattern='cancel'))
async def cancel_button(client, call):
    await cancel_command(client, call.message)


@Client.on_message(filters.private & filters.command(['cancel']))
async def cancel_command(client, message):
    user = await User.get_user(message.chat.id)
    client.stop_listening((message.chat.id, message.from_user.id, message.id))
    text = plate("cancelled", user.chosen_language)
    await Client.edit_message_text(client, chat_id=message.chat.id, message_id=message.id, text=text)


@Client.on_message(filters.private & filters.command(['help']))
async def send_help(client, message):
    user = await User.get_user(message.chat.id)
    text = plate("mainmenu_help_message", user.chosen_language)
    await Client.send_message(client, chat_id=message.chat.id, text=text)


@Client.on_message(filters.private & filters.command(['mydata']))
async def send_mydata(client, message):
    user = await User.get_user(message.chat.id)
    data = await user.create_user_data(technical=True)
    text = plate("mainmenu_your_data_is", user.chosen_language) + data if data \
        else plate("mainmenu_your_data_missing", user.chosen_language)
    await Client.send_message(client, chat_id=message.chat.id, text=text)


@Client.on_message(filters.private & filters.command(['language']))
async def choose_language(_, message):
    user = await User.get_user(message.chat.id)
    text = plate("mainmenu_choose_language", user.chosen_language)
    keyboard = ikb([
        [('🇷🇺Русский', '🇷🇺Русский::language-ru_RU')],
        [('🇬🇧English', '🇬🇧English::language-en_US')]
    ])
    await message.reply(text=text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(pattern='language'))
async def set_language(client, call):
    user = await User.get_user(call.message.chat.id)
    await user.set_attribute("chosen_language", str(call.data).split("-")[1])
    text = str(call.data).split("::")[0] + " " + plate("mainmenu_chosen_language", user.chosen_language)
    await Client.edit_message_text(client, chat_id=call.message.chat.id, message_id=call.message.id, text=text)


@Client.on_callback_query(filters.regex(pattern='send'))
async def send_google(client, call):
    client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))
    if gw is None:
        await Client.delete_messages(client, call.message.chat.id, [call.message.id])
        return
    user = await User.get_user(call.message.chat.id)
    await user.load_attributes()
    await Client.delete_messages(client, call.message.chat.id, call.message.id)

    line = user.user_index
    if not line or type(line) != int:
        line = await User.main_index(get_next=True)
        if line == 2:
            values = [await User.get_attribute_list()]
            send_google = await gw.sheet_write(config.main_sheet, major_dimension="rows",
                                               range_marks=f"a{1}:z{1}", values_list=values)
            if not send_google:
                text_to_admin = plate("registration_send_fail_admin", user.chosen_language)
                await Client.send_message(client, chat_id=config.admins[0], text=text_to_admin)
                return
        await user.set_attribute("user_index", line)

    if user.gender == "male":
        text_gender_part = plate("registration_to_male", user.chosen_language)
    else:
        text_gender_part = plate("registration_to_female", user.chosen_language)
    text = text_gender_part + " " + user.name if user.name else "no data" + "!" + \
                                                                plate("registration_await_result", user.chosen_language)

    await Client.send_message(client, call.message.chat.id, text)

    all_attributes_list = await User.get_attribute_list()
    values = []
    for attr in all_attributes_list:
        values.append(str(await user.get_attribute(attr, setit=False)))
    values = [values]
    send_google = await gw.sheet_write(config.main_sheet, major_dimension="rows",
                                       range_marks=f"a{line}:z{line}", values_list=values)

    text = plate("registration_confirmed", user.chosen_language)
    if not send_google:
        text = plate("registration_failed", user.chosen_language)
        text_to_admin = plate("registration_send_fail_admin", user.chosen_language)
        await Client.send_message(client, chat_id=config.admins[0], text=text_to_admin)
    if send_google:
        await user.set_attribute("is_sent", True)
    await Client.send_chat_action(client, call.message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(5)
    await Client.send_message(client, call.message.chat.id, text)


@Client.on_message(filters.private)
async def kill_trash(client, message):
    if message.media_group_id:
        return
    user = await User.get_user(message.chat.id)
    msg = await message.reply(plate("service_hint", user.chosen_language))
    await asyncio.sleep(1)
    await Client.delete_messages(client, message.chat.id, [message.id, msg.id])
