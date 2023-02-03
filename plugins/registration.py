from main import *


@Client.on_callback_query(filters.regex(pattern='proceed'))
async def proceed_interview(client, call):
    user = await User.get_user(call.message.chat.id)

    step_name = str(call.data).split("_")[1]

    stepper_mark = False

    get_step = Interview.get_step


    if "male" in call.data:
        await user.set_attribute("gender", str(call.data).split("_")[1])
        step = await get_step("gender")
        step = await get_step(step.next)
    else:
        step = await get_step(step_name)

    # creating text ---------------------------------------

    text = await step.get_main_text(user.user_id)
    backward_button = await step.get_previous(user.chosen_language)
    forward_button = await step.get_next(user.chosen_language)
    cancel_button = step.but_cancel
    choice_button1 = step.but_main1
    choice_button2 = step.but_main2

    # creating keyboard -------------------------------------

    keyboard, button_line1, button_line2 = None, None, None

    if forward_button and not backward_button:
        button_line2 = [forward_button, cancel_button]
    elif backward_button and not forward_button:
        button_line2 = [backward_button, cancel_button]
    elif forward_button and backward_button:
        button_line2 = [backward_button, forward_button, cancel_button]

    if choice_button1 and not choice_button2:
        button_line1 = [choice_button1]
    elif choice_button1 and choice_button2:
        button_line1 = [choice_button1, choice_button2]

    if button_line1:
        keyboard = ikb([button_line1, button_line2])
        await user.set_attribute("current_step", None)
    else:
        keyboard = ikb([button_line2])
        stepper_mark = True  # if there is only backward-forward buttons - so we await text input

    if step.kill_all_buttons is True:
        keyboard = None

    # edit mesage    -------------------------------------------

    msg = await Client.edit_message_text(client, call.message.chat.id, call.message.id,
                                         text=text, reply_markup=keyboard, disable_web_page_preview=True)
    if stepper_mark is True:
        await user.set_attribute("current_step", (step.name, msg.chat.id, msg.id))


@Client.on_message()
async def proceed_interviev_text(client, message):
    user = await User.get_user(message.chat.id)

    read_step = await user.get_attribute("current_step")
    if not read_step:
        message.continue_propagation()
        return

    step_name = read_step[0]
    msg = (read_step[1], read_step[2])

    get_step = Interview.get_step

    step = await get_step(step_name)

    if message.text[0] == "/":
        if message.text == "/start" or "/cancel":
            text = plate("cancel", user.chosen_language)
            await Client.edit_message_text(client, chat_id=msg[0], message_id=msg[1], text=text,
                                           disable_web_page_preview=True)
            await user.set_attribute("current_step", None)
            return
        else:
            msg = await message.reply(plate("service_hint2"), user.chosen_language)
            await asyncio.sleep(1)
            await Client.delete_messages(client, message.chat.id, [message.id, msg.id])

    else:
        check = step.datatest if step.datatest is True else step.datatest(message.text)

        if check is not True:
            is_wrong_reply = await Client.send_message(client, message.chat.id, check)
            await asyncio.sleep(3)
            await Client.delete_messages(client, message.chat.id, [message.id, is_wrong_reply.id])

        else:
            await step.apenddata(user, str(step.name)[1:], message.text.replace(";", "").replace("+", ""))

            step = await get_step(step.next)

            stepper_mark = False

            # creating text ---------------------------------------

            text = await step.get_main_text(user.user_id)
            backward_button = await step.get_previous(user.chosen_language)
            forward_button = await step.get_next(user.chosen_language)
            choice_button1 = step.but_main1
            choice_button2 = step.but_main2

            # creating keyboard -------------------------------------

            keyboard, button_line1, button_line2 = None, None, None

            if forward_button and not backward_button:
                button_line2 = [forward_button]
            elif backward_button and not forward_button:
                button_line2 = [backward_button]
            elif forward_button and backward_button:
                button_line2 = [backward_button, forward_button]

            if choice_button1 and not choice_button2:
                button_line1 = [choice_button1]
            elif choice_button1 and choice_button2:
                button_line1 = [choice_button1, choice_button2]

            if button_line1:
                keyboard = ikb([button_line1, button_line2])
                await user.set_attribute("current_step", None)
            else:
                keyboard = ikb([button_line2])
                stepper_mark = True  # if there is only backward-forward buttons - so we await text input

            if step.kill_all_buttons is True:
                keyboard = None

            # edit mesage    -------------------------------------------

            msg = await Client.edit_message_text(client, chat_id=msg[0], message_id=msg[1],
                                                 text=text, reply_markup=keyboard, disable_web_page_preview=True)
            if stepper_mark is True:
                await user.set_attribute("current_step", (step.name, msg.chat.id, msg.id))