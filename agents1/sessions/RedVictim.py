import enum
from agents1.eventUtils import PromptSession
import time

class RedVictimSession(PromptSession):
    class RedVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    # Decision is always the same regardless of trust values but kept for consistency
    class TrustDecision(enum.Enum):
        ASK_HUMAN = 0

    # Trust Belief Thresholds
    WILLINGNESS_THRESHOLD = 0.7
    COMPETENCE_THRESHOLD = 0.7

    # For time estimation
    AVERAGE_MOVE_TIME_PER_TILE = 0.5
    
    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.RedVictimPhase.WAITING_RESPONSE
        
        # Internal flags
        self.rescue_in_progress = False
        self.rescue_time = 50  # e.g. # of ticks needed to 'carry' the victim together
        
        # For trust-based logic
        self.pickup_location = None
        self.goal_vic = None
        self.goal_loc = None
        
        # We store the name for clarity if needed
        self.victim_name = info['obj_id']
        
        print("Red Victim Session Created")

    # Robot found a red victim    
    def robot_continue_rescue(self):
        # Robot continues (or is forced to move on) without human intervention
        print("Robot Continue Rescue for Red Victim")
        self.increment_values("rescue_red", -0.1, 0, self.bot)
        self.delete_self()
        
    def robot_rescue_together(self, ttl=20):
        # Human responded 'Rescue'
        print("Robot Rescue Together heard")
        self.increment_values("rescue_red", 0.15, 0, self.bot)
        # Wait for the human
        self.currPhase = self.RedVictimPhase.WAITING_HUMAN
        # Reset TTL to wait for the human
        self.ttl = ttl
        # Record start time for delivery time tracking
        self.rescue_start_time = time.time()
        # Save pickup location for distance calculation
        if self.bot.state:
            self.pickup_location = (self.bot.state['location'][0], self.bot.state['location'][1])
        # Estimate delivery time based on Manhattan distance
        if self._goal_loc and self.pickup_location:
            self.estimated_delivery_time = self.estimate_delivery_time(self.pickup_location, self._goal_loc)
            print(f"Estimated delivery time: {self.estimated_delivery_time:.2f} seconds")

    # Human found a red victim
    def human_found_red_victim(self):
        pass

    def human_rescue_together(self):
        pass
    
    # Rescue together
    def complete_rescue_together(self):
        print("Completed Red Victim rescue!")
        
        # Check delivery time if available
        if self.rescue_start_time and self.estimated_delivery_time:
            total_time = time.time() - self.rescue_start_time
            
            competence_adjustment = self.calculate_competence_adjustment(total_time, self.estimated_delivery_time)
            
            # Apply the calculated adjustment
            self.increment_values("rescue_red", 0.1, competence_adjustment, self.bot)
            print(f"Delivery completed in {total_time:.2f} seconds (estimated: {self.estimated_delivery_time:.2f})")
            print(f"Competence adjustment: {competence_adjustment:.3f}")
        else:
            # Fallback if timing information isn't available
            self.increment_values("rescue_red", 0.1, 0.1, self.bot)
        
        self.delete_red_victim_session()

    def calculate_competence_adjustment(self, actual_time, estimated_time):
        """
        Calculates competence adjustment based on the ratio of actual to estimated time
        
        Returns a value in range [-0.2, 0.2] where:
        - 0.2 means much faster than expected
        - 0.1 means somewhat faster than expected
        - 0.0 means exactly as expected
        - -0.1 means somewhat slower than expected
        - -0.2 means much slower than expected
        """
        time_ratio = actual_time / estimated_time
        
        if time_ratio <= 0.7:
            return 0.2
        elif time_ratio <= 0.9:
            return 0.1
        elif time_ratio <= 1.1:
            return 0.05
        elif time_ratio <= 1.3:
            return -0.1
        else:
            return -0.2
        
    def manhattan_distance(self, pos1, pos2):
        # Each position should be a tuple (x, y)
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def estimate_delivery_time(self, pickup_location, drop_location):
        distance = self.manhattan_distance(pickup_location, drop_location)
        
        # Buffer time for coordination between human and robot
        coordination_buffer = 10  # seconds
        
        # Estimated time based on distance and average move time
        estimated_time = (distance * self.AVERAGE_MOVE_TIME_PER_TILE) + coordination_buffer
        
        print(f"Manhattan distance: {distance} tiles")
        print(f"Estimated delivery time: {estimated_time:.2f} seconds")
        
        return estimated_time
    
    # For consistency with YellowVictimSession
    def decision_making(self):
        # For Red Victims, decision is always to ask human, regardless of trust values
        competence = self.bot._trustBeliefs[self.bot._human_name]['rescue_red']['competence']
        willingness = self.bot._trustBeliefs[self.bot._human_name]['rescue_red']['willingness']
        
        print(f"Red Victim rescue - competence: {competence}")
        print(f"Red Victim rescue - willingness: {willingness}")
        print("Note: For Red Victims, robot always asks human regardless of trust values")
        
        # Always return ASK_HUMAN for red victims
        return self.TrustDecision.ASK_HUMAN

    def delete_red_victim_session(self):
        self.bot._red_victim_session = None
        print("Red Victim Session Deleted")

    def wait(self):
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.bot._recent_vic is not None and self._goal_vic is None:
            self._goal_vic = self.bot._recent_vic
        
        if (self.bot._goal_vic is not None 
                and self.bot._goal_vic in self.bot._remaining 
                and self._goal_loc is None):
            self._goal_loc = self.bot._remaining[self.bot._goal_vic]
                
        if self.bot._recent_vic is not None and self.recent_vic is None:
            self.recent_vic = self.bot._recent_vic
            
        if self.bot._door['room_name'] is not None and self.room_name is None:
            self.room_name = self.bot._door['room_name']
        
        # Update pickup location if not set yet
        if self.pickup_location is None and self.bot.state:
            self.pickup_location = (self.bot.state['location'][0], self.bot.state['location'][1])
            
            # If we now have both pickup location and goal location, update estimated time
            if self._goal_loc and self.pickup_location:
                self.estimated_delivery_time = self.estimate_delivery_time(self.pickup_location, self._goal_loc)

        # Decrement TTL
        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            return self.on_timeout()
            
        return 0   

    def on_timeout(self):
        if self.currPhase == self.RedVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for response on RED Victim!")
            # Decrease both willingness and competence more strongly
            self.increment_values("rescue_red", -0.15, -0.15, self.bot)
            
            from agents1.OfficialAgent import Phase
            self.bot._send_message(
                f"Picking up Red Victim {self.bot._recent_vic} in {self.bot._door['room_name']}.",
                'RescueBot'
            )
            self.bot._rescue = 'red_alone'
            
            self.bot._answered = True
            self.bot._waiting = False
            self.bot._goal_vic = self.bot._recent_vic
            self.bot._goal_loc = self.bot._remaining[self.bot._goal_vic]
            self.bot._recent_vic = None
            self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
           
            self.delete_red_victim_session()
            return 1
                    
        elif self.currPhase == self.RedVictimPhase.WAITING_HUMAN:
            print("Timed out waiting for human for RED Victim!")
            # Decrease willingness only
            self.increment_values("rescue_red", -0.1, 0, self.bot)

            from agents1.OfficialAgent import Phase
            self.bot._rescue = 'red_alone'
            
            self.bot._send_message(
                f"Picking up {self.recent_vic} in {self.room_name}.", 'RescueBot'
            )
            self.bot._answered = True
            self.bot._waiting = False
            
            self.bot._goal_vic = self._goal_vic
            self.bot._goal_loc = self._goal_loc
            self.bot._recent_vic = None
            
            self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
            self.delete_red_victim_session()
            return 1

        else:
            print("RedVictimSession: Unrecognized phase on timeout!")
            return 0
