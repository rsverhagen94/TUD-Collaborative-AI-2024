import enum
from agents1.eventUtils import PromptSession, Scenario
from actions1.CustomActions import Idle


class StoneObstacleSession(PromptSession):
    count = 0  # Use to calculate confidence
    class StoneObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.StoneObstaclePhase.WAITING_RESPONSE
        self.response_timeout = 200
        self.arrival_timeout = 200
        self.ticks_waited = 0

    def _reset_bot_state(self, next_phase=None):
        """Helper method to reset bot state variables consistently"""
        self.bot._answered = True
        self.bot._waiting = False
        self.bot._remove = False
        if next_phase:
            self.bot._phase = next_phase

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

        VERY_LOW_COMPETENCE_THRESHOLD = -0.2
        VERY_LOW_WILLINGNESS_THRESHOLD = -0.3
        if (bot._trustBeliefs[bot._human_name]['remove_stone']['competence'] < VERY_LOW_COMPETENCE_THRESHOLD or
                bot._trustBeliefs[bot._human_name]['remove_stone']['willingness'] < VERY_LOW_WILLINGNESS_THRESHOLD):
            # If we have low competence and willingness beliefs for the human, remove the stone immediately
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
        """User chooses to skip the stone obstacle"""
        from agents1.OfficialAgent import Phase
        
        print("Continue Stone heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", -0.1, 0, self.bot)
        
        # Add area to the to-do list and set next phase
        self.bot._to_search.append(self.bot._door['room_name'])
        self._reset_bot_state(Phase.FIND_NEXT_GOAL)
        self.delete_self()

    def remove_alone(self):
        """User wants the bot to remove the stones alone"""
        from agents1.OfficialAgent import Phase
        
        print("Remove Alone heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.1, 0, self.bot)
        
        self._reset_bot_state(Phase.ENTER_ROOM)
        self.delete_self()

    def remove_together(self):
        """User wants to remove the stones together - prepare to wait for human"""
        print("Remove Together heard")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.15, 0, self.bot)
        
        # Reset wait timer and set waiting phase
        self.currPhase = self.StoneObstaclePhase.WAITING_HUMAN
        self.ticks_waited = 0
        self.bot._send_message('Please come to ' + str(self.bot._door['room_name']) + ' to remove stones together.', 'RescueBot')

    # Static method for removal when no prompt is generated as the human asked the bot to remove an obstacle
    @staticmethod
    def help_remove_together(bot, info, ttl=200):
        if not isinstance(bot._current_prompt, StoneObstacleSession):
            print("Attaching a new StoneObstacleSession")
            # Attach a new session to the bot
            curr_session = StoneObstacleSession(bot, info, ttl)
            curr_session.currPhase = StoneObstacleSession.StoneObstaclePhase.WAITING_HUMAN
            bot._current_prompt = curr_session
        return bot._current_prompt.wait()

    def complete_remove_together(self):
        """Complete removal after human arrives and helps"""
        from agents1.OfficialAgent import Phase
        
        print("Completed removal together!")
        if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
            self.increment_values("remove_stone", 0.1, 0.2, self.bot)
        
        self._reset_bot_state(Phase.ENTER_ROOM)
        self.delete_self()

    def on_timeout(self):
        """Handle timeout for response or arrival"""
        from agents1.OfficialAgent import Phase, RemoveObject
        
        message = ""
        if self.currPhase == self.StoneObstaclePhase.WAITING_RESPONSE:
            print("Timed out waiting for response about stones!")
            if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
                self.increment_values("remove_stone", -0.15, -0.15, self.bot)
            
            message = "No response about removing the stones. I'll remove them alone and proceed."
            self.bot._send_message(message, "RescueBot")
            self._reset_bot_state(Phase.ENTER_ROOM)
            self.delete_self()
            return RemoveObject.__name__, {'object_id': self.info['obj_id']}

        elif self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN:
            print("Timed out waiting for human to arrive for stone removal!")
            if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
                self.increment_values("remove_stone", -0.1, 0, self.bot)
            
            message = "We agreed to remove stones together, but you didn't arrive in time. I'll remove them alone and proceed."
            self.bot._send_message(message, "RescueBot")
            self._reset_bot_state(Phase.ENTER_ROOM)
            self.delete_self()
            return RemoveObject.__name__, {'object_id': self.info['obj_id']}

        else:
            print("Unexpected phase in timeout!")
            self.delete_self()
            return Idle.__name__, {'duration_in_ticks': 10}

    def wait(self):
        """Handle waiting states and timeouts"""
        self.ticks_waited += 1
        
        # Check timeout based on current phase
        if (self.currPhase == self.StoneObstaclePhase.WAITING_RESPONSE and self.ticks_waited >= self.response_timeout) or \
           (self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN and self.ticks_waited >= self.arrival_timeout):
            return self.on_timeout()
        
        # Check if human has arrived when waiting for them
        if self.currPhase == self.StoneObstaclePhase.WAITING_HUMAN:
            state = self.bot.state
            if state and state.get({'is_human_agent': True}):
                print("Human arrived to help with stone removal!")
                if self.scenario_used == Scenario.USE_TRUST_MECHANISM:
                    self.increment_values("remove_stone", 0.05, 0.1, self.bot)
                self.bot._send_message('Thank you for coming to help with the stones! Press D to remove them.', 'RescueBot')
                # Note: We don't complete removal here - waiting for the D key press which is handled in the main loop
        
        # Still waiting
        return None, {}
    
    def delete_self(self):
        """Clean up session reference"""
        if hasattr(self.bot, '_current_prompt') and self.bot._current_prompt is self:
            self.bot._current_prompt = None
            print("Stone obstacle session deleted successfully")
        else:
            print("Warning: Could not delete stone obstacle session - reference not found")


    def increment_values(self, task, willingness, competence, bot):
        StoneObstacleSession.count += 1
        print("Confidence:", self.get_confidence())
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness",
                         self.get_confidence() * willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence",
                         self.get_confidence() * competence)

    def get_confidence(self):
        return min(1.0, max(0.0, StoneObstacleSession.count / 2))
