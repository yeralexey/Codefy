from main import *


@Client.on_message(filters.private & filters.command(['start']))
async def send_welcome_on_command(client, message):
    user = await User.get_user(user_id=message.chat.id, user_name=message.from_user.username, set_active=True)
    text = plate("mainmenu_welcome_message", user.chosen_language)
    keyboard = ikb([[(plate("registration_button", user.chosen_language), 'proceed_lastname')]])
    await Client.send_message(client, chat_id=message.chat.id, text=text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(pattern='main_start'))
async def send_welcome_on_call(client, call):
    client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))
    user = await User.get_user(call.message.chat.id)
    text = plate("mainmenu_welcome_message", user.chosen_language)
    keyboard = ikb([[(plate("registration_button", user.chosen_language), 'proceed_lastname')]])
    await Client.edit_message_text(client, chat_id=call.message.chat.id, message_id=call.message.id,
                                   text=text, reply_markup=keyboard)


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
async def choose_language(client, message):
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
