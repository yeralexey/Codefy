from main import *


@Client.on_message(filters.private & filters.command(['start']))
async def send_welcome_on_command(client, message):
    user = await User.get_user(user_id=message.from_user.id)
    if user == "ask":
        user = await User.get_user(user_id=message.from_user.id, user_name=message.from_user.username,
                                   first_boot=True)
    text = "Please, [readme](https://telegra.ph/Codefy-guide-02-10) at first!"
    await Client.send_message(client, chat_id=message.chat.id, text=text)

    text = "Done?"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="Confirm",
            callback_data="i_confirm"
        )

    ]])
    await Client.send_message(client, chat_id=message.chat.id, text=text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("i_confirm"))
async def about_inline(client, call):
    user = await User.get_user(user_id=call.message.chat.id)  # is able in private chat only, receives bot as "from"
    await Client.delete_messages(client, chat_id=call.message.chat.id, message_ids=call.message.id)
    text = plate("mainmenu_inline_message", user.chosen_language)
    await Client.send_message(client, chat_id=call.message.chat.id, text=text, disable_web_page_preview=True)
