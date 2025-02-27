import enum
from abc import abstractmethod

# Class to manage which prompt was last encountered by the bot
class PromptSession:
    def __init__(self, bot, ttl=100):
        self.bot = bot
        self.ttl = ttl

    @abstractmethod
    def wait(self): pass
    @abstractmethod
    def on_timeout(self): pass

    def delete_self(self):
        self.bot._current_prompt = None

    @staticmethod
    def increment_values(task, willingness, competence, bot):
        # TODO: implement this later
        # bot._willingness += willingness
        # bot._competence += competence
        pass

class StoneObstacleSession(PromptSession):
    class StoneObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, ttl=-1):
        super().__init__(bot, ttl)
        self.currPhase = self.StoneObstaclePhase.WAITING_RESPONSE

    def removeAlone(self):
        print("Removing alone")
        self.increment_values("remove_stone", 0.1, 0, self.bot)
        self.delete_self()

    def continueStone(self):
        print("Continue Stone heard")
        self.increment_values("remove_stone", -0.1, 0, self.bot)
        self.delete_self()

    def removeTogether(self, ttl=100):
        print("Remove Together heard")
        self.increment_values("remove_stone", 0.1, 0, self.bot)
        # Wait for the human
        self.currPhase = self.StoneObstaclePhase.WAITING_HUMAN
        # Reset ttl
        self.ttl = ttl


    def completeRemoveTogether(self):
        self.increment_values("remove_stone", 0.1, 0.2, self.bot)
        self.delete_self()

    def wait(self):
        self.ttl -= 1
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)
        if self.ttl == 0:
            self.on_timeout()

    def on_timeout(self):
        # Figure out what to do depending on the current phase
        if self.currPhase == self.StoneObstaclePhase.WAITING_RESPONSE:
            print("Timed out waiting for response!")
            # TODO: penalize?
            self.increment_values("remove_stone", -0.1, 0, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            # Add area to the to do list
            self.bot._to_search.append(self.bot._door['room_name'])

            # TODO: is this a good idea?!
            from agents1.OfficialAgent import Phase
            self.bot._phase = Phase.FIND_NEXT_GOAL

        elif self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN:
            print("Timed out waiting for human!")
            self.increment_values("remove_stone", -0.1, 0, self.bot)
            self.delete_self()

        else:
            #How did you even get here?!
            pass

#TODO: Implement Confidence Level