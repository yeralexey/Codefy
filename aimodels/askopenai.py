import openai
from main import config
openai.api_key = config.openai_key

from utils.logger import init_logger
ailogger = init_logger(name="openai", console_level="ERROR")


def ask_code(question):
    model = "code-davinci-002"
    try:
        result = openai.Completion.create(
            model=model,
            prompt=question,
            temperature=0,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["#Task"]
        )

        ailogger.info(f"\n{question}")
        result_final = result["choices"][0]["text"]
        while result_final[-1] == "#" or result_final[-1] == " ":
            result_final = result_final[:-1]
        if len(result_final) < 20:
            result_final = "!!! inappropriate generation:"+"\n\n"+str(result)


    except openai.error.RateLimitError:
        result_final = "Sorry, we are out of the limit for now, try later..."
    except Exception as err:
        ailogger.exception(err)
        result_final = err

    return result_final