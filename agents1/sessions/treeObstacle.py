import enum
from agents1.eventUtils import PromptSession, Scenario

class TreeObstacleSession(PromptSession):
    def __init__(self, bot, info, ttl=100):
        super().__init__(bot, info, ttl)

    @staticmethod
    def process_trust(bot, info):
        if super().scenario_used == Scenario.ALWAYS_TRUST:
            return None
        elif super().scenario_used == Scenario.NEVER_TRUST:
            bot._answered = True
            bot._waiting = False
            bot._send_message('Removing tree blocking ' + str(bot._door['room_name']) + '.',
                              'RescueBot')
            from agents1.OfficialAgent import Phase, RemoveObject
            bot._phase = Phase.ENTER_ROOM
            bot._remove = False

            return RemoveObject.__name__, {'object_id': info['obj_id']}


        LOW_COMPETENCE_THRESHOLD = 0.1
        LOW_WILLINGNESS_THRESHOLD = 0.1

        if bot._trustBeliefs[bot._human_name]['remove_tree']['competence'] > LOW_COMPETENCE_THRESHOLD:
            return None

        if bot._trustBeliefs[bot._human_name]['remove_tree']['willingness'] > LOW_WILLINGNESS_THRESHOLD:
            return None

        # If we have low competence and willingness beliefs for the human, remove the tree immediately
        bot._answered = True
        bot._waiting = False
        bot._send_message('Removing tree blocking ' + str(bot._door['room_name']) + '.',
                               'RescueBot')
        from agents1.OfficialAgent import Phase, RemoveObject
        bot._phase = Phase.ENTER_ROOM
        bot._remove = False

        return RemoveObject.__name__, {'object_id': info['obj_id']}

    def continue_tree(self):
        print("Continue Tree heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_tree", -0.1, 0, self.bot)
        self.delete_self()

    def remove_tree(self):
        print("Remove Tree heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_tree", 0.1, 0, self.bot)
        self.delete_self()

    def on_timeout(self):
        print("Timed out waiting for response!")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
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