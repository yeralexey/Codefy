from main import *


@Client.on_callback_query(filters.regex(pattern='cancel'))
async def cancel_button(client, call):
    user = await User.get_user(call.message.chat.id)
    await user.set_attribute("current_step", None)
    text = plate("cancelled", user.chosen_language)
    await Client.edit_message_text(client, chat_id=call.message.chat.id, message_id=call.message.id, text=text)


@Client.on_message(filters.private & filters.command(['cancel']))
async def cancel_command(client, message):
    user = await User.get_user(message.chat.id)
    read_step = await user.get_attribute("current_step")
    if not read_step:
        msg = await message.reply(plate("cancelled_nothing", user.chosen_language))
        await asyncio.sleep(1)
        await Client.delete_messages(client, message.chat.id, [message.id, msg.id])
        return
    text = plate("cancelled", user.chosen_language)
    step_name, call_message_chat, call_message_id = read_step[0], read_step[1], read_step[2]
    await Client.edit_message_text(client, chat_id=call_message_chat, message_id=call_message_id, text=text)
    await user.set_attribute("current_step", None)


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


# @Client.on_message(filters.private)
# async def kill_trash(client, message):
#     if message.media_group_id:
#         return
#     user = await User.get_user(message.chat.id)
#     msg = await message.reply(plate("service_hint", user.chosen_language))
#     await asyncio.sleep(1)
#     await Client.delete_messages(client, message.chat.id, [message.id, msg.id])
