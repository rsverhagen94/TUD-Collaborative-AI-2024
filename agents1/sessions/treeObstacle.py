import enum
from agents1.eventUtils import PromptSession


class TreeObstacleSession(PromptSession):
    def __init__(self, bot, ttl=100):
        super().__init__(bot, ttl)

    def continue_tree(self):
        print("Continue Tree heard")
        self.increment_values("remove_tree", -0.1, 0, self.bot)
        self.delete_self()

    def remove_tree(self):
        print("Remove Tree heard")
        self.increment_values("remove_tree", 0.1, 0, self.bot)
        self.delete_self()

    def wait(self):
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            self.on_timeout()

    def on_timeout(self):
        print("Timed out waiting for response!")
        self.increment_values("remove_tree", -0.15, -0.15, self.bot)

        self.bot._answered = True
        self.bot._waiting = False
        # Add area to the to do list
        self.bot._to_search.append(self.bot._door['room_name'])

        from agents1.OfficialAgent import Phase
        self.bot._phase = Phase.FIND_NEXT_GOAL
        self.delete_self()

#TODO: Implement Confidence Level