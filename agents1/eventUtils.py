import enum
from abc import abstractmethod


# Class to manage which prompt was last encountered by the bot
class PromptSession:
    def __init__(self, bot, info, ttl=100):
        self.bot = bot
        self.info = info  # Store info about the current object (used for directing removal)
        self.ttl = ttl  # How long the prompt should wait for a response (not wait for a human to show up!)

    def wait(self):
        # Updates the ttl of the prompt every time it is called
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            # Direct the bot to perform an action if the prompt's time to live has expired
            return self.on_timeout()

        # Do nothing if the prompt still has time to live
        return None, {}

    @abstractmethod
    def on_timeout(self): pass

    def delete_self(self):
        self.bot._current_prompt = None

    @staticmethod
    def increment_values(task, willingness, competence, bot):
        # Update trust beliefs for a particular task by defined increments
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness", willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence", competence)
