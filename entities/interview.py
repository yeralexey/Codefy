from .userdata import User

from utils import plate

from utils.logger import init_logger
logger = init_logger("entities.interview")


class Interview:
    """
    A class representing an interview step,  previous and next  steps. Each step also has buttons for proceeding,
    canceling, and confirming. The class also has a dictionary and list for storing all the interview steps,
    and a method for getting the current step by name. In this example - instances are created in
    /plugins/registration.py, for collecting users personal data.
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

    async def get_main_text(self, user_id):
        user = await User.get_user(user_id)
        text = plate(f"interview_ask_{self.name}", user.chosen_language)
        if self.send_data is False:
            return text
        else:
            data = await user.create_user_data(self.name)
            return f'{data}\n\n**{text}**'

    @classmethod
    async def get_step(cls, key):
        return cls.interview_dict[key]


# class AskGirls(Interview):
#     pass
#
# class AskBoys(Interview):
#     pass
