import enum
from agents1.eventUtils import PromptSession
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
        print("Completed removal!")
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
            self.increment_values("remove_stone", -0.1, -0.1, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            # Add area to the to do list
            self.bot._to_search.append(self.bot._door['room_name'])

            # TODO: is this a good idea?!
            from agents1.OfficialAgent import Phase
            self.bot._phase = Phase.FIND_NEXT_GOAL
            self.delete_self()

        elif self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN:
            print("Timed out waiting for human!")
            self.increment_values("remove_stone", -0.1, 0, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            # Add area to the to do list
            self.bot._to_search.append(self.bot._door['room_name'])

            # TODO: is this a good idea?!
            from agents1.OfficialAgent import Phase
            self.bot._phase = Phase.FIND_NEXT_GOAL
            self.delete_self()


        else:
            #How did you even get here?!
            pass

#TODO: Implement Confidence Level