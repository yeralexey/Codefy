from .userdata import User
from pyromod.helpers import ikb
from utils import plate

from utils.logger import init_logger
logger = init_logger("entities.interview")


class Interview:
    """
    A class representing an interview step,  previous and next  steps. Each step also has buttons for proceeding,
    canceling, and confirming. The class also has a dictionary and list for storing all the interview steps,
    and a method for getting the current step by name. In this example - instances are created in
    /plugins/registration.py, for collecting users personal data.

    Commented classes below - are examples, how different Interview branches can be set up. Simply inherit class
    Interview, and create instances. Certain corrections should be done in plugins/registration.py, so in proceeds not
    Interview steps but from inherited classes ones.

    class AskGirls(Interview):
        pass

    class AskBoys(Interview):
        pass

    """

    interview_dict = {}
    interview_list = []

    def __init__(self, name):
        if not hasattr(self.__class__, 'interview_dict'):
            self.__class__.interview_dict = {}
            self.__class__.interview_list = []
        i_dict = self.__class__.interview_dict
        i_list = self.__class__.interview_list
        self.name = name
        self.user = User.get_user
        self.apenddata = User.set_attribute
        self.datatest = True
        self.previous = None
        self.next = None
        self.kill_all_buttons = None
        self.but_main1 = None
        self.but_main2 = None
        self.send_data = True
        self.but_cancel = ("❌", "cancel")
        i_dict[name] = self
        i_list.append(name)
        index = i_list.index(name)
        if index != 0:
            setattr(self, 'previous', i_list[index-1])
            i_dict[i_list[index-1]].set_attribute('next', name)

    def set_attribute(self, attr, value):
        setattr(self, attr, value)

    async def get_previous(self, language):
        backward_button = plate(f"button_backward", language)
        if self.previous:
            return backward_button, f'proceed_{self.previous}'
        else:
            return backward_button, "main_start"

    async def get_next(self, language):
        if self.next:
            forward_button = plate(f"button_forward", language)
            return forward_button, f'proceed_{self.next}'
        else:
            return "OK ☑️", "send"

    async def get_text(self, user_id):
        user = await User.get_user(user_id)
        text = plate(f"interview_ask_{self.name}", user.chosen_language)
        if self.send_data is False:
            return text
        else:
            data = await user.create_user_data(self.name)
            return f'{data}\n\n**{text}**'

    async def get_keyboard(self, language):

        backward_button = await self.get_previous(language)
        forward_button = await self.get_next(language)
        cancel_button = self.but_cancel
        choice_button1 = self.but_main1
        choice_button2 = self.but_main2

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
            step_flag = False   # if buttons to be used as input, no need to create text await
        else:
            keyboard = ikb([button_line2])
            step_flag = True   # if there is only backward-forward buttons - so we await text input

        if self.kill_all_buttons is True:
            keyboard = None

        if not self.next:
            step_flag = False  # if it is last iteration, no input text is awaited in current configuration

        return keyboard, step_flag

    @classmethod
    async def get_step(cls, key):
        return cls.interview_dict[key]
