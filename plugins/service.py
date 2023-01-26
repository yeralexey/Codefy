from main import *


@Client.on_message(filters.private)
async def kill_trash(client, message):
    if message.media_group_id:
        return
    user = await User.get_user(message.chat.id)
    msg = await message.reply(plate("service_hint", user.chosen_language))
    await asyncio.sleep(1)
    await Client.delete_messages(client, message.chat.id, [message.id, msg.id])
