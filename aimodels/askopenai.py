import openai
from main import config
openai.api_key = config.openai_key

from utils.logger import init_logger
ailogger = init_logger(name="openai", console_level="ERROR")

from functools import wraps


def log_it(func):
    @wraps(func)
    async def wrapper(question, identificator, prompt_final):
        ailogger.info(f"{identificator} - {question}")
        result = await func(question, identificator, prompt_final)
        try:
            text = result["choices"][0]["text"]
            if len(text) > 10:
                ailogger.info(f"{identificator} - {text}")
            else:
                ailogger.info(f"{identificator} - {result}")
        except Exception as err:
            ailogger.error(f"{identificator} - {err}")
        return result
    return wrapper


@log_it
async def ask_davinci(question, user_id, prompt_final):
    model = "text-davinci-003"
    result = openai.Completion.create(
        prompt=question + prompt_final,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=model
    )
    return result


@log_it
async def ask_curie(question, user_id, prompt_final):
    model = "text-curie-001"
    result = openai.Completion.create(
        prompt=question,
        temperature=0.8,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=model
    )
    return result


@log_it
async def ask_code(question, user_id, prompt_final):
    model = "code-davinci-002"
    result = openai.Completion.create(
        model=model,
        prompt=question,
        temperature=0,
        max_tokens=1200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )
    return result


async def ask_dalle(question):
    image = openai.Image()
    result = image.create(
        prompt=question,
        n=1,
        size="512x512").data[0].url
    return result


# text: davinci-003, curie-001, babbage-001, ada-001
# code: davinci-002, cushman-001