from main import *


@Client.on_callback_query(filters.regex(pattern='proceed'))
async def proceed_interview(client, call):

    user = await User.get_user(call.message.chat.id)
    client.stop_listening((call.message.chat.id, call.message.from_user.id, call.message.id))

    if "male" in call.data:
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

            try:
                answer = await call.message.chat.listen(timeout=30)
            except listen.ListenerStopped:
                return
            except listen.ListenerTimeout:
                return
            except Exception as err:
                logger.exception(err)
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
                