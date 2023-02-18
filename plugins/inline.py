from main import *
from pyrogram import ContinuePropagation
from aimodels import askopenai
from utils.nekobin import *
from uuid import uuid4
nekobin = NekoBin()
uuid = str(uuid4())

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


async def task_index(get_next=False, value=None):
    if value is not None:
        if isinstance(value, int):
            return await db.write_raw("task_index", value)
    result = await db.read_raw("task_index") or 1
    if get_next:
        result += 1
        await db.write_raw("task_index", result)
    return result


async def fix_proper_comment(text, language):
    langs_slash_comment = ["C++", "C#", "Go", "Golang", "C", "Java", "JavaScript", "PHP", "Swift", "Kotlin", "Rust"]
    if language in langs_slash_comment:
        text = text.replace("#", "//")
    if language == "C#":
        text = text.replace("C//", "C#")
    return text


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
                    id=uuid,
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
async def inline_result_func(client, inline_result):

    # Checking type of inline_result

    if inline_result.result_id != uuid:
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
        if prog_lang.lower() == "php":
            prog_lang = "PHP"
        elif prog_lang.lower() == "javascript":
            prog_lang = "JavaScript"
        elif prog_lang.lower() == "coffeescript":
            prog_lang = "CoffeeScript"
        else:
            prog_lang = prog_lang.title()
        del words_list[arg_index]
        del words_list[arg_index]
        query = " ".join(words_list)
    else:
        prog_lang = "Python"
        query = inline_result.query

    # Creating await message

    text = f"Generating function, that will `{query}`, on {prog_lang}."

    try:
        await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                      disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as err:
        logger.exception(err)

    # Processing a query text, asking for generation and creating text of function

    stopper = "#Task ##"
    index = await task_index(get_next=True)
    question = f"###Task {index}. Write just one function using {prog_lang} programming language. It should {query}." \
               f"\n#Use readable laconic code according to {prog_lang} highest standards." \
               f"\n#Add documentation with detailed function explain." \
               f"\n#Provide typehints, if {prog_lang} supports." \
               f"\n#Add one how-to-call example." \
               f"\n#My function:"
    question = await fix_proper_comment(question, prog_lang)
    stopper = await fix_proper_comment(stopper, prog_lang)
    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, askopenai.ask_code, question, stopper)

    answer = answer.replace("\n+", "\n").replace("`", "")

    if '"""' in answer:
        in_code_result = str(answer).replace('`', '').replace('"""', '~~~', 1). \
            replace('"""', '\n    by @CodefyBot, t.me \n    """').replace('~~~', '"""')
        in_code_result = f"```\n{in_code_result}```"
    else:

        in_code_result = f"```\n\n# by @CodefyBot, t.me\n{answer}\n```"
        in_code_result = await fix_proper_comment(in_code_result, prog_lang)

    # Creating Telegram post

    text = f"**request**: \"`{inline_result.query}`\"\n" \
           f"**author**: {author}\n" \
           f"**language**: {prog_lang}" \
           f"\n{in_code_result}\n<i>Use [neko:bin](https://www.nekobin.com)</i>"

    if len(text) > 4000:
        text = f"{text[:2000]}...```\n<i>Use [neko:bin](https://www.nekobin.com)</i>"

    try:
        await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                      disable_web_page_preview=True, reply_markup=None)
    except Exception as err:
        print(err)
        logger.exception(err)


@Client.on_callback_query(filters.regex("inline_remove"))
async def in_line_callback(client, call):
    text = "removed..."
    await Client.edit_inline_text(client, inline_message_id=call.inline_message_id, text=text)
