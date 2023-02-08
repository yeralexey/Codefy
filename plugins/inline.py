from main import *
from utils.nekobin import *
from uuid import uuid4
nekobin = NekoBin()


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
                description="Elegant and open-source pastebin service, Paste, save and share the link of your text "
                            "content using a sleek and intuitive interface!",
                input_message_content=InputTextMessageContent("Generating...⏳"),
                id=str(uuid4()),
                thumb_url="https://nekobin.com/static/img/nekobin.jpg",
                thumb_width=5,
                thumb_height=5,
                url="Nekobin.com",
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
async def in_line_result(client, inline_result):
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