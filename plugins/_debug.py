from main import *

"""
Set of handlers used on debug, named so to be indexed with Pyrogram Smart Plugins being first.
"""


@Client.on_callback_query()
async def print_callback(client, call):
    """
    To check buttons failure on debug. Outputs button callback data.
    """
    logger.debug(call.data)
    call.message.continue_propagation()