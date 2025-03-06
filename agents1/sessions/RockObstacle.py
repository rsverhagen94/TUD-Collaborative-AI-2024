import enum
from agents1.eventUtils import PromptSession

class RockObstacleSession(PromptSession):
    class RockObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.RockObstaclePhase.WAITING_RESPONSE
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

    def continue_rock(self):
        """User chooses to skip the rock obstacle"""
        from agents1.OfficialAgent import Phase

        print("Continue Rock heard")
        self.increment_values("remove_rock", -0.1, 0, self.bot)
        self.bot._skipped_obstacles.append(self.info['obj_id'])
        self.bot._to_search.append(self.bot._door['room_name'])
        self._reset_bot_state(Phase.FIND_NEXT_GOAL)
        self.delete_self()

    def remove_rock(self):
        """User wants to remove the rock together"""
        print("Remove Rock heard")
        self.increment_values("remove_rock", 0.1, 0, self.bot)
        self.currPhase = self.RockObstaclePhase.WAITING_HUMAN
        self.ticks_waited = 0
        self.bot._send_message('Please come to ' + str(self.bot._door['room_name']) + ' to remove the big rock together.', 'RescueBot')

    def complete_remove_rock(self):
        """Complete rock removal and prepare for next phase"""
        from agents1.OfficialAgent import Phase

        print("Completing rock removal")
        self.increment_values("remove_rock", 0.1, 0.2, self.bot)
        self._reset_bot_state(Phase.ENTER_ROOM)
        self.delete_self()

    def on_timeout(self):
        """Handle timeout for response or arrival"""
        from agents1.OfficialAgent import Phase
        from actions1.CustomActions import Idle

        message = ""
        if self.currPhase == self.RockObstaclePhase.WAITING_RESPONSE:
            print("Timed out waiting for response about the big rock!")
            self.increment_values("remove_rock", -0.15, -0.15, self.bot)
            message = "No response about removing the big rock. I'll skip this area and continue searching elsewhere."
        else:  # WAITING_HUMAN
            print("Timed out waiting for human to arrive for big rock removal!")
            self.increment_values("remove_rock", -0.1, -0.1, self.bot)
            message = "We agreed to remove the big rock together, but you didn't arrive in time. I'll skip this area and search elsewhere."
        
        self.bot._send_message(message, "RescueBot")
        self.bot._skipped_obstacles.append(self.info['obj_id'])
        self.bot._to_search.append(self.bot._door['room_name'])
        self._reset_bot_state(Phase.FIND_NEXT_GOAL)
        self.delete_self()
        return Idle.__name__, {'duration_in_ticks': 25}

    def wait(self):
        """Handle waiting states and timeouts"""
        self.ticks_waited += 1
        
        # Check timeout based on current phase
        if (self.currPhase == self.RockObstaclePhase.WAITING_RESPONSE and self.ticks_waited >= self.response_timeout) or \
           (self.currPhase == self.RockObstaclePhase.WAITING_HUMAN and self.ticks_waited >= self.arrival_timeout):
            return self.on_timeout()
        
        # Check if human has arrived when waiting for them
        if self.currPhase == self.RockObstaclePhase.WAITING_HUMAN:
            state = self.bot.state
            if state and state.get({'is_human_agent': True}):
                print("Human arrived to help with rock removal!")
                self.increment_values("remove_rock", 0.05, 0.1, self.bot)
                self.bot._send_message('Thank you for coming to help with the rock!', 'RescueBot')
                self.bot._answered = True
                self.bot._waiting = False
        
        # Still waiting
        return None, {}
    
    def delete_self(self):
        """Clean up session reference"""
        if hasattr(self.bot, '_rock_obstacle_session') and self.bot._rock_obstacle_session is self:
            self.bot._rock_obstacle_session = None
            if hasattr(self.bot, '_current_prompt') and self.bot._current_prompt is self:
                self.bot._current_prompt = None
            print("Rock obstacle session deleted successfully")
        else:
            print("Warning: Could not delete rock obstacle session - reference not found")