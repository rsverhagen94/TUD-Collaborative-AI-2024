import enum
from agents1.eventUtils import PromptSession


class TreeObstacleSession(PromptSession):
    def __init__(self, bot, info, ttl=100):
        super().__init__(bot, info, ttl)

    def continue_tree(self):
        print("Continue Tree heard")
        self.increment_values("remove_tree", -0.1, 0, self.bot)
        self.delete_self()

    def remove_tree(self):
        print("Remove Tree heard")
        self.increment_values("remove_tree", 0.1, 0, self.bot)
        self.delete_self()

    def on_timeout(self):
        print("Timed out waiting for response!")
        self.increment_values("remove_tree", -0.15, -0.15, self.bot)

        self.bot._answered = True
        self.bot._waiting = False
        self.bot._send_message('Removing tree blocking ' + str(self.bot._door['room_name']) + '.',
                           'RescueBot')
        from agents1.OfficialAgent import Phase, RemoveObject
        self.bot._phase = Phase.ENTER_ROOM
        self.bot._remove = False

        self.delete_self()

        return RemoveObject.__name__, {'object_id': self.info['obj_id']}

#TODO: Implement Confidence Level