import enum, time, math
from agents1.eventUtils import PromptSession

class RedVictimSession(PromptSession):
    number_of_actions = 0
    class RedVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1
        IN_PROGRESS = 2

    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.RedVictimPhase.WAITING_RESPONSE
        
        self._goal_vic = None
        self._goal_loc = None
        
        self.recent_vic = None
        self.room_name = None
        
        # For measuring how long the rescue takes
        self.rescue_start_time = None
        self.pickup_location = None
        self.estimated_delivery_time = None

    @staticmethod
    def calculate_time_proximity_scale(actual_time, estimated_time, max_deviation=20):
        """
        Calculate a scaling factor (0..1) based on how close actual_time is to estimated_time.
        If time_diff <= max_deviation, produce a value between 0..1 (logarithmic).
        If far beyond max_deviation, return -1 (indicating a big negative penalty).
        """
        time_diff = abs(actual_time - estimated_time)
        if time_diff <= max_deviation:
            # Logarithmic scaling so small differences give near 1.0, bigger differences yield smaller factors
            return 1 - math.log(time_diff + 1) / math.log(max_deviation + 1)
        else:
            # Too large a deviation => negative signal
            return -1

    def modify_competence_by_time(self, actual_time, estimated_time, number_of_actions=0, use_confidence=False):
        """
        Compare actual_time to estimated_time and do a trust update:
          - If actual_time is near or below estimate => raise competence/willingness
          - If it's way above => reduce them
        """
        time_scale = self.calculate_time_proximity_scale(actual_time, estimated_time)
        if time_scale >= 0:
            # Good performance => positive
            competence_change = 0.1 * time_scale
            willingness_change = 0.05 * time_scale
            
            if use_confidence:
                competence_change = self.calculate_increment_with_confidence(self.number_of_actions, competence_change)
                willingness_change = self.calculate_increment_with_confidence(self.number_of_actions, willingness_change)
                
            self.increment_values("rescue_red", willingness_change, competence_change, self.bot)
        else:
            # Very late => negative
            competence_change = -0.1
            willingness_change = -0.05
            
            if use_confidence:
                competence_change = self.calculate_increment_with_confidence(self.number_of_actions, competence_change)
                willingness_change = self.calculate_increment_with_confidence(self.number_of_actions, willingness_change)
                
            self.increment_values("rescue_red", willingness_change, competence_change, self.bot)

    def robot_rescue_together(self, ttl=200, number_of_actions=0, use_confidence=False):
        """
        Called when the user (or agent) chooses "Rescue" for a critically injured Red Victim.
        """
        print("Robot Rescue Together heard.")
        # Slight willingness bump for choosing "Rescue"
        
        increment_value = 0.15
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(self.number_of_actions, increment_value)
            
        self.increment_values("rescue_red", increment_value, 0, self.bot)

        # Store the victim we're rescuing - critically important
        if self.bot._recent_vic is not None:
            self._goal_vic = self.bot._recent_vic
        self.bot._goal_vic = self._goal_vic

        # Identify the drop zone from the agent's _remaining dictionary, if any
        if self._goal_vic in getattr(self.bot, "_remaining", {}):
            self._goal_loc = self.bot._remaining[self._goal_vic]
            self.bot._goal_loc = self._goal_loc

        # Transition to WAITING_HUMAN for up to `ttl` ticks
        self.currPhase = self.RedVictimPhase.WAITING_HUMAN
        self.ttl = ttl
        self.rescue_start_time = time.time()

        # Optionally store the robot's current location to guess an ETA
        my_loc = None
        if (
            hasattr(self.bot, "agent_properties") and
            "location" in self.bot.agent_properties and
            self.bot.agent_properties["location"] is not None
        ):
            my_loc = self.bot.agent_properties["location"]

        if my_loc:
            self.pickup_location = tuple(my_loc)

        # Estimate time from pickup to drop-off 
        if self._goal_loc and self.pickup_location:
            self.estimated_delivery_time = self.estimate_delivery_time(self.pickup_location, self._goal_loc)
            print(f"Estimated delivery time: {self.estimated_delivery_time:.2f} seconds")

        # Send a message to remind the user they need to arrive within a time limit
        self.bot._send_message(
            f"You've chosen to rescue {self._goal_vic}. You have 20 seconds to arrive at my location to help carry the victim.",
            "RescueBot"
        )

    def robot_continue_rescue(self, number_of_actions=0, use_confidence=False):
        """
        Called if the human or agent decides "Continue," i.e. skip this Red Victim for now.
        That implies a willingness penalty for ignoring a severely injured victim.
        """
        print("Robot Continue Rescue heard.")
        
        increment_value = -0.15
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(self.number_of_actions, increment_value)
            
        self.increment_values("rescue_red", increment_value, 0, self.bot)
        self.delete_self()

    def wait(self, number_of_actions=0, use_confidence=False):
        """
        Called each tick. Decrement TTL and handle transitions.
        """
        # Update local tracking variables if needed
        if self.bot._recent_vic is not None and self._goal_vic is None:
            self._goal_vic = self.bot._recent_vic
        if self.bot._door['room_name'] is not None and self.room_name is None:
            self.room_name = self.bot._door['room_name']

        # Print status every 5 ticks for debugging
        if self.ttl % 5 == 0 and self.ttl > 0:
            print(f"Red victim session TTL: {self.ttl}")

        if self.ttl > 0:
            self.ttl -= 1
            if self.ttl == 0:
                return self.on_timeout(self.number_of_actions, use_confidence)
                
        # If we are waiting for the human physically after they said "Rescue"
        # if self.currPhase == self.RedVictimPhase.WAITING_HUMAN:
        #     if self.check_human_proximity():
        #         self.human_showed_up(number_of_actions, use_confidence)
        #         self.currPhase = self.RedVictimPhase.IN_PROGRESS
        #         # Once the user is here, no further timeouts for arrival
        #         self.ttl = -1
        #         return 0
              
        # Only show warning message if we're waiting for initial response
        if self.currPhase == self.RedVictimPhase.WAITING_RESPONSE:
            # When ttl gets low, display a warning message
            if self.ttl == 50:  # About 10 seconds left
                self.bot._send_message(
                    f"Please respond within 10 seconds whether to rescue {self.bot._recent_vic} or I'll continue searching.",
                    "RescueBot"
                )
        return 0

    def on_timeout(self, number_of_actions=0, use_confidence=False):
        """
        Called if we run out of time in WAITING_RESPONSE or WAITING_HUMAN.
        """        
        if self.currPhase == self.RedVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for Red Victim decision!")

            willingness_increment = -0.2
            competence_increment = -0.1
            
            if use_confidence:
                willingness_increment = self.calculate_increment_with_confidence(number_of_actions, willingness_increment)
                competence_increment = self.calculate_increment_with_confidence(number_of_actions, competence_increment)
                
            # Larger penalty because user did not answer at all
            self.increment_values("rescue_red", willingness_increment, competence_increment, self.bot)
            self.bot._send_message(
                f"No response received. Continuing to search without rescuing {self.bot._recent_vic} in {self.bot._door['room_name']}.",
                "RescueBot"
            )
            self.bot._answered = True
            self.bot._waiting = False
            self.bot._rescue = None
            
            # Add the victim to todo list to potentially rescue later
            if self.bot._recent_vic not in self.bot._todo:
                self.bot._todo.append(self.bot._recent_vic)

            from agents1.OfficialAgent import Phase
                
            # Reset recent_vic and explicitly set phase to FIND_NEXT_GOAL
            temp_vic = self.bot._recent_vic
            self.bot._recent_vic = None
            self.bot._phase = Phase.FIND_NEXT_GOAL
            
            # Delete session after all bot state changes
            self.delete_self()
            print(f"RedVictimSession timeout completed - moved on from {temp_vic}")
            return 1
            
        elif self.currPhase == self.RedVictimPhase.WAITING_HUMAN:
            print("Timed out waiting for human to arrive! Human did not show up in time.")
            willingness_increment = -0.1
            competence_increment = -0.05
            
            if use_confidence:
                willingness_increment = self.calculate_increment_with_confidence(self.number_of_actions, willingness_increment)
                competence_increment = self.calculate_increment_with_confidence(self.number_of_actions, competence_increment)
                
            # Slightly smaller penalty than ignoring from the start
            self.increment_values("rescue_red", willingness_increment, competence_increment, self.bot)
            self.bot._send_message(
                f"You did not arrive in time to rescue {self._goal_vic} in {self.room_name}. Continuing to search without rescuing this victim.",
                "RescueBot"
            )
            self.bot._answered = True
            self.bot._waiting = False
            
            # Add the victim to todo list to potentially rescue later
            if self.bot._goal_vic not in self.bot._todo:
                self.bot._todo.append(self.bot._goal_vic)

            from agents1.OfficialAgent import Phase
                
            # Reset these variables to allow the robot to continue searching
            temp_vic = self.bot._goal_vic
            self.bot._goal_vic = None
            self.bot._goal_loc = None
            self.bot._rescue = None
            self.bot._phase = Phase.FIND_NEXT_GOAL
            
            # Delete session after all bot state changes
            self.delete_self()
            print(f"RedVictimSession timeout completed - moved on from {temp_vic}")
            return 1
        else:
            print("on_timeout called, but we are in an unknown phase. No action taken.")
            return 1

    def check_human_proximity(self):
        """
        Check if the human agent is close to the victim.
        This would be called from the wait method while in WAITING_HUMAN phase.
        """
        # Implement logic to check if human is near the victim
        # This should return True if the human is in proximity, False otherwise
        # Could use state information or other mechanisms depending on your implementation
        
        # Example placeholder implementation - replace with actual logic:
        for info in self.bot._state_tracker.get_state().values():
            if 'is_human_agent' in info and info['is_human_agent']:
                # Check if human is in the same room as the victim
                if self.room_name in str(info.get('room_name', '')):
                    return True
        return False

    def human_showed_up(self, number_of_actions=0, use_confidence=False):
        """
        Called when the human arrives at the victim location.
        Updates trust values positively.
        """
        # Human showed up to help as promised
        
        willingness_increment = 0.05
        competence_increment = 0.1
        
        if use_confidence:
            willingness_increment = self.calculate_increment_with_confidence(self.number_of_actions, willingness_increment)
            competence_increment = self.calculate_increment_with_confidence(self.number_of_actions, competence_increment)
            
        self.increment_values("rescue_red", willingness_increment, competence_increment, self.bot)
        self.bot._send_message(
            f"Thank you for coming to help rescue {self._goal_vic}! Let's work together.",
            "RescueBot"
        )

    def complete_rescue_together(self, number_of_actions=0, use_confidence=False):
        """
        Called once the Red Victim is successfully dropped off at the drop zone.
        We finalize rescue time measurements and do final trust updates.
        """
        if self.rescue_start_time:
            total_time = time.time() - self.rescue_start_time
            if self.estimated_delivery_time:
                self.modify_competence_by_time(total_time, self.estimated_delivery_time, self.number_of_actions, use_confidence)
            print(f"Total rescue time for Red Victim: {total_time:.2f} seconds")

        print("Completed rescue of Red Victim together!")
        
        willingness_increment = 0.1
        competence_increment = 0.2
        
        if use_confidence:
            willingness_increment = self.calculate_increment_with_confidence(self.number_of_actions, willingness_increment)
            competence_increment = self.calculate_increment_with_confidence(self.number_of_actions, competence_increment)
            
        # Increase willingness & competence further now that rescue is done
        self.increment_values("rescue_red", willingness_increment, competence_increment, self.bot)
        self.delete_self()

    def delete_red_victim_session(self):
        """
        Manually delete this session object if needed (e.g., from the agent code).
        """
        print("Red Victim Session Deleted")
        self.bot._red_victim_session = None

    def estimate_delivery_time(self, start, end):
        """
        A simple manhattan-distance-based guess for how many seconds
        a pickup + drop might take. E.g., 1 second per tile as a default.
        """
        x1, y1 = start
        x2, y2 = end
        dist = abs(x1 - x2) + abs(y1 - y2)
        return dist * 1.0
    
    def delete_self(self):
        """
        Properly clean up the session reference from the bot.
        """
        if hasattr(self.bot, '_red_victim_session') and self.bot._red_victim_session is self:
            self.bot._red_victim_session = None
            print("Red victim session deleted successfully")
        else:
            print("Warning: Could not delete red victim session - reference not found")

    def increment_values(self, task, willingness, competence, bot):
        RedVictimSession.number_of_actions += 1
        # Update trust beliefs for a particular task by defined increments
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness", willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence", competence)