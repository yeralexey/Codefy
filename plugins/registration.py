"""
All Interview instances from questionary.py are processed with these two functions. Step is chosen by callback data
if processed by buttons, and by fsm-like algorithm, with step saved in database, as user's attribute.
"""

from main import *


@Client.on_callback_query(filters.regex(pattern='proceed'))
async def proceed_interview(client, call):
    user = await User.get_user(call.message.chat.id)
    step_name = str(call.data).split("_")[1]
    get_step = Interview.get_step  # inherited from Interview class can be defined if needed

    if "male" in call.data:  # all callbacks need to be processed here
        await user.set_attribute("gender", str(call.data).split("_")[1])
        step = await get_step("gender")
        step = await get_step(step.next)
    else:
        step = await get_step(step_name)

    text = await step.get_text(user.user_id)
    keyboard, step_flag = await step.get_keyboard(user.chosen_language)

    call_message = await Client.edit_message_text(client, call.message.chat.id, call.message.id,
                                                  text=text, reply_markup=keyboard, disable_web_page_preview=True)
    if step_flag:
        await user.set_attribute("current_step", (step.name, call_message.chat.id, call_message.id))
    else:
        await user.set_attribute("current_step", None)


@Client.on_message(filters.private)
async def proceed_interview_text(client, message):
    user = await User.get_user(message.chat.id)

    read_step = await user.get_attribute("current_step")
    if not read_step:
        message.continue_propagation()
        return

    step_name, call_message_chat, call_message_id = read_step[0], read_step[1], read_step[2]
    get_step = Interview.get_step  # inherited from Interview class can be defined if needed
    step = await get_step(step_name)

    if message.text[0] == "/":
        if message.text == "/start" or message.text == "/cancel":
            text = plate("cancelled", user.chosen_language)
            await Client.edit_message_text(client, chat_id=call_message_chat, message_id=call_message_id, text=text,
                                           disable_web_page_preview=True)
            await user.set_attribute("current_step", None)
            return
        else:
            msg = await message.reply(plate("service_hint2"), user.chosen_language)
            await asyncio.sleep(1)
            await Client.delete_messages(client, message.chat.id, [message.id, msg.id])

    else:
        check = step.datatest if step.datatest is True else step.datatest(message.text, user.chosen_language)

        if check is not True:
            is_wrong_reply = await Client.send_message(client, message.chat.id, check)
            await asyncio.sleep(3)
            await Client.delete_messages(client, message.chat.id, [message.id, is_wrong_reply.id])

        else:
            await step.apenddata(user, step.name, message.text.replace(";", "").replace("+", ""))

            step = await get_step(step.next)
            text = await step.get_text(user.user_id)
            keyboard, step_flag = await step.get_keyboard(user.chosen_language)

            await Client.delete_messages(client, message.chat.id, message.id)

            call_message = await Client.edit_message_text(client, call_message_chat, call_message_id, text=text,
                                                          reply_markup=keyboard, disable_web_page_preview=True)
            if step_flag:
                await user.set_attribute("current_step", (step.name, call_message.chat.id, call_message.id))
            else:
                await user.set_attribute("current_step", None)
