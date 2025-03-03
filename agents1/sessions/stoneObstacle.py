import enum
from agents1.eventUtils import PromptSession, Scenario


class StoneObstacleSession(PromptSession):
    class StoneObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.StoneObstaclePhase.WAITING_RESPONSE

    @staticmethod
    def process_trust(bot, info):
        if PromptSession.scenario_used == Scenario.ALWAYS_TRUST:
            return None
        elif PromptSession.scenario_used == Scenario.NEVER_TRUST:
            bot._answered = True
            bot._waiting = False
            bot._send_message('Removing stones blocking ' + str(bot._door['room_name']) + '.',
                              'RescueBot')
            from agents1.OfficialAgent import Phase, RemoveObject
            bot._phase = Phase.ENTER_ROOM
            bot._remove = False

            return RemoveObject.__name__, {'object_id': info['obj_id']}

        LOW_COMPETENCE_THRESHOLD = 0.1
        LOW_WILLINGNESS_THRESHOLD = 0.1

        if(bot._trustBeliefs[bot._human_name]['remove_stone']['competence'] > LOW_COMPETENCE_THRESHOLD):
            return None

        if (bot._trustBeliefs[bot._human_name]['remove_stone']['willingness'] > LOW_WILLINGNESS_THRESHOLD):
            return None

        # If we have low competence and willingness beliefs for the human, remove the stone immediately
        bot._answered = True
        bot._waiting = False
        bot._send_message('Removing stones blocking ' + str(bot._door['room_name']) + '.',
                               'RescueBot')
        from agents1.OfficialAgent import Phase, RemoveObject
        bot._phase = Phase.ENTER_ROOM
        bot._remove = False

        return RemoveObject.__name__, {'object_id': info['obj_id']}

    def continue_stone(self):
        print("Continue Stone heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", -0.1, 0, self.bot)
        self.delete_self()

    def remove_alone(self):
        print("Remove Alone heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.1, 0, self.bot)
        self.delete_self()

    def remove_together(self, ttl=100):
        print("Remove Together heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.15, 0, self.bot)
        # Wait for the human
        self.currPhase = self.StoneObstaclePhase.WAITING_HUMAN
        # Reset ttl
        self.ttl = ttl

    def complete_remove_together(self):
        print("Completed removal!")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.1, 0.2, self.bot)
        self.delete_self()

    def on_timeout(self):
        # Figure out what to do depending on the current phase
        if self.currPhase == self.StoneObstaclePhase.WAITING_RESPONSE:
            print("Timed out waiting for response!")
            if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
                self.increment_values("remove_stone", -0.15, -0.15, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            self.bot._send_message('Removing stones blocking ' + str(self.bot._door['room_name']) + '.',
                               'RescueBot')
            from agents1.OfficialAgent import Phase, RemoveObject
            self.bot._phase = Phase.ENTER_ROOM
            self.bot._remove = False

            self.delete_self()
            return RemoveObject.__name__, {'object_id': self.info['obj_id']}

        elif self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN:
            print("Timed out waiting for human!")
            if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
                self.increment_values("remove_stone", -0.1, 0, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            self.bot._send_message('Removing stones blocking ' + str(self.bot._door['room_name']) + '.',
                                   'RescueBot')
            from agents1.OfficialAgent import Phase, RemoveObject
            self.bot._phase = Phase.ENTER_ROOM
            self.bot._remove = False

            self.delete_self()
            return RemoveObject.__name__, {'object_id': self.info['obj_id']}


        else:
            print("How did you even get here?!")
            pass

#TODO: Implement Confidence Level