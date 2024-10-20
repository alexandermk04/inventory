from telegram.ext.filters import UpdateFilter
from telegram import Update

class PollFilter(UpdateFilter):

    def __init__(self):
        super().__init__
        self.name = 'POLL_FILTER'

    def filter(self, update: Update):
        print(update)
        return update.poll_answer is not None