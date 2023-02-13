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
    user = await User.get_user(user_id=call.message.from_user.id)
    if user == "ask":
        user = await User.get_user(user_id=call.message.from_user.id, user_name=call.message.from_user.username,
                                   first_boot=True)
    await Client.delete_messages(client, chat_id=call.message.chat.id, message_ids=call.message.id)
    text = plate("mainmenu_inline_message", user.chosen_language)
    await Client.send_message(client, chat_id=call.message.chat.id, text=text, disable_web_page_preview=True)


    # channel = -1001796429321
    #
    # text = "**Codefy**\n" \
    #        "├ @CodefyBot\n" \
    #        "├ @CodefyChat\n" \
    #        "├ @CodefyChannel\n" \
    #        "└  [readme](https://telegra.ph/Codefy-guide-02-10)"
    #
    # keyboard = InlineKeyboardMarkup([[
    #     InlineKeyboardButton(
    #         text="Generate",
    #         url="https://t.me/CodefyBot"
    #     )
    # ]])
    #
    # await Client.edit_message_caption(client, chat_id=channel, caption=text, message_id=28, reply_markup=keyboard)



# @Client.on_callback_query(filters.regex(pattern='main_start'))
# async def send_welcome_on_call(client, call):
#     user = await User.get_user(call.message.chat.id)
#     await user.set_attribute("current_step", None)
#     text = plate("mainmenu_welcome_message", user.chosen_language)
#     keyboard = ikb([[(plate("registration_button", user.chosen_language), 'proceed_lastname')]])
#     await Client.edit_message_text(client, chat_id=call.message.chat.id, message_id=call.message.id,
#                                    text=text, reply_markup=keyboard)
