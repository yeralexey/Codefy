from main import *

name = Interview("lastname")  # first question should in callback, in button, starting registration "proceed_lastname"
name.datatest = vd.is_letter

name = Interview("name")
name.datatest = vd.is_letter

name = Interview("patronymic")
name.datatest = vd.is_letter

email = Interview("email")
email.datatest = vd.is_email

phone = Interview("phone")
phone.datatest = vd.is_phone

passport = Interview("passport")

regaddress = Interview("regaddress")

gender = Interview("gender")
gender.but_main1 = ('🕺', 'proceed_male')
gender.but_main2 = ('💃', 'proceed_female')

confirm = Interview("confirm")

listener_debug_counter = 0


@Client.on_callback_query(filters.regex(pattern='proceed'))
async def proceed_interview(client, call):

    user = await User.get_user(call.message.chat.id)
    client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))

    if "cancel" in call.data:
        client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))
        text = plate("registration_cancelled", user.chosen_language)
        await Client.edit_message_text(client, chat_id=call.message.chat.id, message_id=call.message.id, text=text)
        return
    elif "male" in call.data:
        await user.set_attribute("gender", str(call.data).split("_")[1])
        step = await Interview.get_step("gender")
        step = await Interview.get_step(step.next)
    else:
        step = await Interview.get_step(str(call.data).split("_")[1])

    asking = True
    while asking is True:
        text = await step.get_main_text(call.message.chat.id)
        backward_button = await step.get_previous(user.chosen_language)
        forward_button = await step.get_next(user.chosen_language)
        cancel_button = step.but_cancel
        choice_button1 = step.but_main1
        choice_button2 = step.but_main2

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
            questiontype = "button"
            keyboard = ikb([button_line1, button_line2])
        else:
            questiontype = "input"
            keyboard = ikb([button_line2])

        new = True
        checking = True
        while checking is True and asking is True:
            if new:
                await Client.edit_message_text(client, call.message.chat.id, call.message.id, text,
                                               reply_markup=keyboard,
                                               disable_web_page_preview=True)
            if questiontype == "button":
                return

            global listener_debug_counter
            try:
                listener_debug_counter += 1
                logger.debug(f"listener enabled - {user.user_id} - {listener_debug_counter}")
                answer = await call.message.chat.listen(timeout=30)
                listener_debug_counter -= 1
                logger.debug(f"listener finished - {user.user_id} - {listener_debug_counter}")
            except listen.ListenerStopped:
                listener_debug_counter -= 1
                logger.debug(f"listener stopped - {user.user_id} - {listener_debug_counter}")
                return
            except listen.ListenerTimeout:
                listener_debug_counter -= 1
                logger.debug(f"listener timeout - {user.user_id} - {listener_debug_counter}")
                return
            except Exception as err:
                logger.exception(err)
                listener_debug_counter -= 1
                logger.debug(f"listener failed - {user.user_id} - {listener_debug_counter}")
                return

            check = step.datatest if step.datatest is True else step.datatest(answer.text, user.chosen_language)

            if check is not True:
                client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))
                is_wrong_reply = await Client.send_message(client, call.message.chat.id, check)
                await asyncio.sleep(3)
                await Client.delete_messages(client, call.message.chat.id, [answer.id, is_wrong_reply.id])
                new = False

            elif answer.text[0] == "/":
                msg = await answer.reply(plate("service_hint2", user.chosen_language))
                await asyncio.sleep(1)
                await Client.delete_messages(client, call.message.chat.id, [answer.id, msg.id])
                new = False

            else:
                await step.apenddata(user, step.name, answer.text.replace(";", "").replace("+", ""))
                step = await Interview.get_step(step.next)
                await Client.delete_messages(client, call.message.chat.id, [answer.id])
                checking = False


@Client.on_callback_query(filters.regex(pattern='send'))
async def send_google(client, call):
    user = await User.get_user(call.message.chat.id)
    client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))
    await user.load_attributes()
    await Client.delete_messages(client, call.message.chat.id, call.message.id)

    if user.join_date is None:
        await user.set_attribute("join_date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
