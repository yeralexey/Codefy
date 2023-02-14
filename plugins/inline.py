from main import *
from pyrogram import ContinuePropagation
from aimodels import askopenai
from utils.nekobin import *
from uuid import uuid4
nekobin = NekoBin()
neko_uid = str(uuid4()) # TODO Findgood way to generate one for all, but to generate inside inline_answer - to many calcs?...
python_uid = str(uuid4())


# TODO Refactored, dry fails.


async def nekobin_it(content, title="test function", author="CodeAiBot"):
    try:
        neko = await nekobin.nekofy(
            content=content,
            title=title,
            author=author
        )
    except HostDownError:
        return "Host is down at the moment"
    except TooFastError:
        return "Too many requests"

    if neko.url[-4:] != "None":
        return neko.url
    else:
        return "Nekobin.com refuse, flood wait."


@Client.on_inline_query()
async def inline_answer(client, inline_query):
    user = await User.get_user(user_id=inline_query.from_user.id, set_active=False)
    if user == "ask":
        user = await User.get_user(user_id=inline_query.from_user.id, user_name=inline_query.from_user.username,
                                   first_boot=True, set_active=False)

    if user.is_active is None or user.is_active is False:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="Please,",
                    description='activate Codefy, go to bot dialogue and run "/start".'
                                '\nJoin the movement towards a better code!',
                    input_message_content=InputTextMessageContent("[Welcome!](https://t.me/CodefyBot)"),
                    thumb_url="https://raw.githubusercontent.com/yeralexey/Codefy/master/maindata/icons/"
                              "share_icn.jpg",
                    thumb_width=5,
                    thumb_height=5,

                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                "Activate",
                                url="https://t.me/CodefyBot"
                            )]
                        ]
                    )
                ),

            ],
            cache_time=1
        )

    else:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="Generate function,",
                    description='with docstrings and typehints. Simply continue "function, that will..."',
                    input_message_content=InputTextMessageContent(plate("inline_generating", user.chosen_language)),
                    id=python_uid,
                    thumb_url="https://raw.githubusercontent.com/yeralexey/Codefy/master/maindata/icons/"
                              "func_icn.jpg",
                    thumb_width=5,
                    thumb_height=5,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                plate("button_cancel", user.chosen_language),
                                callback_data="inline_remove"
                            )]
                        ]
                    )
                ),


                InlineQueryResultArticle(
                    title="Paste nekobin.com,",
                    description="save and share the link of your python code  in elegant way, len(code)<500.",
                    input_message_content=InputTextMessageContent(plate("inline_generating", user.chosen_language)),
                    id=neko_uid,
                    thumb_url="https://raw.githubusercontent.com/yeralexey/Codefy/master/maindata/icons/"
                              "nb_icn.jpg",
                    thumb_width=5,
                    thumb_height=5,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                plate("button_cancel", user.chosen_language),
                                callback_data="inline_remove"
                            )]
                        ]
                    )
                ),

                InlineQueryResultArticle(
                    title="Share Codefy,",
                    description="help people to join the movement towards a better code!",
                    input_message_content=InputTextMessageContent("[Welcome to](https://t.me/CodefyChannel/28)"),
                    thumb_url="https://raw.githubusercontent.com/yeralexey/Codefy/master/maindata/icons/"
                              "share_icn.jpg",
                    thumb_width=5,
                    thumb_height=5,

                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                "Join",
                                url="https://t.me/CodefyChannel/28"
                            )]
                        ]
                    )
                ),

            ],
            cache_time=1
        )


@Client.on_chosen_inline_result()
async def inline_result_neko(client, inline_result):
    if inline_result.result_id != neko_uid:
        raise ContinuePropagation

    user = await User.get_user(user_id=inline_result.from_user.id)

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                plate("button_cancel", user.chosen_language),
                callback_data="inline_remove"
            )]
        ]
    )

    # Checking query before processing

    if len(str(inline_result.query)) < 25:
        text = plate("inline2_insufficient_description")
        try:
            await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                          disable_web_page_preview=True, reply_markup=reply_markup)
        except Exception as err:
            logger.exception(err)
        return


    result = await nekobin_it(content=inline_result.query, author=user.user_name)

    try:
        await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=result,
                                      disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as err:
        logger.exception(err)


@Client.on_chosen_inline_result()
async def inline_result_func(client, inline_result):

    # Checking type of inline_result

    if inline_result.result_id != python_uid:
        raise ContinuePropagation

    # Defining user

    user = await User.get_user(user_id=inline_result.from_user.id)

    # Cancel Button

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                plate("button_cancel", user.chosen_language),
                callback_data="inline_remove"
            )]
        ]
    )

    # Checking query before processing

    if len(str(inline_result.query)) < 25:
        text = plate("inline_insufficient_description")
        try:
            await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                          disable_web_page_preview=True, reply_markup=reply_markup)
        except Exception as err:
            logger.exception(err)
        return

    # Defining author

    if inline_result.from_user.username == "None":
        author = "anonymous"
    else:
        author = f"@{inline_result.from_user.username}"

    # Defining lanquage and configuring query

    words_list = str(inline_result.query).split(" ")

    if "-l" in words_list:
        arg_index = words_list.index("-l")
        lang_index = arg_index + 1
        prog_lang = words_list[lang_index]
        del words_list[arg_index]
        del words_list[arg_index]
        query = " ".join(words_list)
    else:
        prog_lang = "Python"
        query = inline_result.query

    # Creating await message

    text = f"Generating function, that will `{query}`."

    try:
        await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                      disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as err:
        logger.exception(err)

    # Processing a query text, asking for generation and creating text of function

    if prog_lang == "Python":

        question = f"###Write a function on {prog_lang} programming language, with typehints and high quality " \
               f"docstrings, explaining what the function does and how to use it, that will {query}:"
    else:
        question = f"###Write a function on {prog_lang} programming language, that will {query}:"

    answer = await askopenai.ask_code(question=question, identificator=f"test~{user.user_id}", prompt_final=None)
    answer = answer["choices"][0]["text"]

    raw_result = str(answer).replace('`', '').replace('"""', '~~~', 1).\
        replace('"""', '\n       by @CodefyBot \n    """').replace('~~~', '"""')

    in_code_result = f"```{raw_result}```"

    # Pasting text of function to nekobin.com, trying to receive link

    try:
        neko_link = await nekobin_it(content=raw_result, author=user.user_name)
        if prog_lang == "Python":
            if "htt" in str(neko_link):
                neko_link = f"{neko_link}.py"
    except Exception as err:
        logger.exception(err)
        neko_link = "necobin.com fail"

    # Creating Telegram post

    text = f"**request**: \"`{inline_result.query}`\"\n" \
           f"**author**: {author}\n" \
           f"**language**: {prog_lang}" \
           f"{in_code_result}<i>{neko_link}</i>"

    try:
        await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                      disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as err:
        logger.exception(err)


@Client.on_callback_query(filters.regex("inline_remove"))
async def in_line_callback(client, call):
    text = "removed..."
    await Client.edit_inline_text(client, inline_message_id=call.inline_message_id, text=text)
