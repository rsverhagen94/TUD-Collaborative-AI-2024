import enum
from agents1.eventUtils import PromptSession

class RockObstacleSession(PromptSession):
    count_actions = 0
    
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

    def continue_rock(self, number_of_actions=0, use_confidence=False):
        """User chooses to skip the rock obstacle"""
        from agents1.OfficialAgent import Phase

        print("Continue Rock heard")
        
        increment_value = -0.1
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("remove_rock", increment_value, 0, self.bot)
        self.bot._skipped_obstacles.append(self.info['obj_id'])
        self.bot._to_search.append(self.bot._door['room_name'])
        self._reset_bot_state(Phase.FIND_NEXT_GOAL)
        self.delete_self()

    def remove_rock(self, number_of_actions=0, use_confidence=False):
        """User wants to remove the rock together"""
        print("Remove Rock heard")
        
        increment_value = 0.1
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("remove_rock", increment_value, 0, self.bot)
        self.currPhase = self.RockObstaclePhase.WAITING_HUMAN
        self.ticks_waited = 0
        self.bot._send_message('Please come to ' + str(self.bot._door['room_name']) + ' to remove the big rock together.', 'RescueBot')

    def complete_remove_rock(self, number_of_actions=0, use_confidence=False):
        """Complete rock removal and prepare for next phase"""
        from agents1.OfficialAgent import Phase

        print("Completing rock removal")
        
        willingness_increment = 0.1
        competence_increment = 0.2
        
        if use_confidence:
            willingness_increment = self.calculate_increment_with_confidence(number_of_actions, willingness_increment)
            competence_increment = self.calculate_increment_with_confidence(number_of_actions, competence_increment)
            
        self.increment_values("remove_rock", willingness_increment, competence_increment, self.bot)
        self._reset_bot_state(Phase.ENTER_ROOM)
        self.delete_self()

    def on_timeout(self, number_of_actions=0, use_confidence=False):
        """Handle timeout for response or arrival"""
        from agents1.OfficialAgent import Phase
        from actions1.CustomActions import Idle

        message = ""
        willingness_increment = -0.15
        competence_increment = -0.15
        
        if use_confidence:
            willingness_increment = self.calculate_increment_with_confidence(number_of_actions, willingness_increment)
            competence_increment = self.calculate_increment_with_confidence(number_of_actions, competence_increment)
            
        if self.currPhase == self.RockObstaclePhase.WAITING_RESPONSE:
            print("Timed out waiting for response about the big rock!")
            message = "No response about removing the big rock. I'll skip this area and continue searching elsewhere."
        else:  # WAITING_HUMAN
            print("Timed out waiting for human to arrive for big rock removal!")
            # Slightly different penalties for not showing up vs. not responding
            willingness_increment = -0.1 if not use_confidence else self.calculate_increment_with_confidence(number_of_actions, -0.1)
            competence_increment = -0.1 if not use_confidence else self.calculate_increment_with_confidence(number_of_actions, -0.1)
            message = "We agreed to remove the big rock together, but you didn't arrive in time. I'll skip this area and search elsewhere."
        
        self.increment_values("remove_rock", willingness_increment, competence_increment, self.bot)
        self.bot._send_message(message, "RescueBot")
        self.bot._skipped_obstacles.append(self.info['obj_id'])
        self.bot._to_search.append(self.bot._door['room_name'])
        self._reset_bot_state(Phase.FIND_NEXT_GOAL)
        self.delete_self()
        return Idle.__name__, {'duration_in_ticks': 25}

    def wait(self, number_of_actions=0, use_confidence=False):
        """Handle waiting states and timeouts"""
        self.ticks_waited += 1
        
        # Print status every 5 ticks for debugging
        if self.ticks_waited % 5 == 0:
            print(f"Rock obstacle session waiting: {self.ticks_waited} ticks")
        
        # Check timeout based on current phase
        if (self.currPhase == self.RockObstaclePhase.WAITING_RESPONSE and self.ticks_waited >= self.response_timeout) or \
           (self.currPhase == self.RockObstaclePhase.WAITING_HUMAN and self.ticks_waited >= self.arrival_timeout):
            return self.on_timeout(number_of_actions, use_confidence)
        
        # Check if human has arrived when waiting for them
        if self.currPhase == self.RockObstaclePhase.WAITING_HUMAN:
            state = self.bot.state
            if state and state.get({'is_human_agent': True}):
                print("Human arrived to help with rock removal!")
                
                willingness_increment = 0.05
                competence_increment = 0.1
                
                if use_confidence:
                    willingness_increment = self.calculate_increment_with_confidence(number_of_actions, willingness_increment)
                    competence_increment = self.calculate_increment_with_confidence(number_of_actions, competence_increment)
                
                self.increment_values("remove_rock", willingness_increment, competence_increment, self.bot)
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
            print("Rock obstacle session deleted")
        else:
            print("Warning: Could not delete rock obstacle session - reference not found")
            
    def increment_values(self, task, willingness, competence, bot):
        RockObstacleSession.count_actions += 1
        print("Confidence:", self.get_confidence())
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness",
                         self.get_confidence() * willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence",
                         self.get_confidence() * competence)

    def get_confidence(self):
        return min(1.0, max(0.0, RockObstacleSession.count_actions / 2))