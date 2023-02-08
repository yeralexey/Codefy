from main import *
from utils.nekobin import *
from uuid import uuid4
nekobin = NekoBin()
neko_uid = str(uuid4())
python_uid = str(uuid4())
from pyrogram import ContinuePropagation

from aimodels import askopenai



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
        return neko.url + ".py"
    else:
        return "Nekobin.com refuse, flood wait."


@Client.on_inline_query()
async def inline_answer(client, inline_query):
    user = await User.get_user(user_id=inline_query.from_user.id)
    if user == "ask":
        user = await User.get_user(user_id=inline_query.from_user.id, user_name=inline_query.from_user.username,
                                   first_boot=True)
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="Nekobin.com",
                description="Paste, save and share the link of your python code  in elegant way. (len(code)<500)",
                input_message_content=InputTextMessageContent("Generating...⏳"),
                id=neko_uid,
                thumb_url="https://nekobin.com/static/img/nekobin.jpg",
                thumb_width=5,
                thumb_height=5,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            "Powered by Nekobin.com",
                            url="https://Nekobin.com"
                        )]
                    ]
                )
            ),
            InlineQueryResultArticle(
                title="Python function",
                description='Create python function, complete phrase "Function, that..."',
                input_message_content=InputTextMessageContent("Generating...⏳"),
                id=python_uid,
                thumb_url="https://i.pinimg.com/564x/4d/13/d5/4d13d55d6d0b38b7a4e85fcf97ff6279.jpg",
                thumb_width=5,
                thumb_height=5,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            "Powered by Nekobin.com",
                            url="https://Nekobin.com"
                        )]
                    ]
                )
            )
        ],
        cache_time=1
    )


@Client.on_chosen_inline_result()
async def in_line_result_neko(client, inline_result):
    if inline_result.result_id != neko_uid:
        raise ContinuePropagation
        return

    user = await User.get_user(user_id=inline_result.from_user.id)
    code_to_paste = inline_result.query
    result = await nekobin_it(content=code_to_paste, author=user.user_name)

    # reply_markup = InlineKeyboardMarkup(
    #     [
    #         [InlineKeyboardButton(
    #             "Open in Nekobin.com",
    #             url=f"{result}"
    #         )]
    #     ]
    # )

    await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=result,
                                  disable_web_page_preview=True)
    # await Client.edit_inline_reply_markup(client, inline_message_id=inline_result.inline_message_id,
    #                                       reply_markup=None)




@Client.on_chosen_inline_result()
async def in_line_result(client, inline_result):
    if inline_result.result_id != python_uid:
        raise ContinuePropagation
        return

    user = await User.get_user(user_id=inline_result.from_user.id)

    if len(str(inline_result.query)) < 25:
        text = "provide sufficient description, more 25 chars"
    else:
        question = f"###Write a python function with an elaborate, high quality docstrings, explaining what the " \
                   f"function does and how to use it, that {inline_result.query}:"

        answer = await askopenai.ask_code(question=question, identificator=f"test~{user.user_id}", prompt_final=None)
        answer = answer["choices"][0]["text"]
        answer = f"```{str(answer).replace('`', '')}```"

        result = await nekobin_it(content=answer, author=user.user_name)
        text = f"Function,that **{inline_result.query}:**\n{answer}\n\n{result}"

    await Client.edit_inline_text(client, inline_message_id=inline_result.inline_message_id, text=text,
                                  disable_web_page_preview=True)
    # await Client.edit_inline_reply_markup(client, inline_message_id=inline_result.inline_message_id,
    #                                       reply_markup=None)




