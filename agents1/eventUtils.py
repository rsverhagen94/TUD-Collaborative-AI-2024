import enum
from abc import abstractmethod

# Class to manage which prompt was last encountered by the bot
class PromptSession:
    def __init__(self, bot, info, ttl=100):
        self.bot = bot
        self.info = info # Store info about the current object (used for directing removal)
        self.ttl = ttl # Store

    def wait(self):
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            return self.on_timeout()

        return None, {}
    @abstractmethod
    def on_timeout(self): pass

    def delete_self(self):
        self.bot._current_prompt = None

    @staticmethod
    def increment_values(task, willingness, competence, bot):
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness", willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence", competence)
