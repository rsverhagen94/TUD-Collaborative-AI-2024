import enum
from agents1.eventUtils import PromptSession
import time

class RedVictimSession(PromptSession):
    class RedVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    # Trust Belief Thresholds
    WILLINGNESS_THRESHOLD = 0.7
    COMPETENCE_THRESHOLD = 0.7
    
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

    def robot_rescue_together(self, ttl=100):
        """
        User responded 'Rescue' on a critically injured Red Victim.
        This is roughly analogous to 'rescueYellow' => 'Rescue Together'.
        """
        print("Robot Rescue Together heard")
        
        # Increase Willingness slightly for Red Victim
        self.increment_values("rescue_red", 0.15, 0, self.bot)
        
        # If we want to do a path planning, let's store the victim & location right now:
        if self.bot._recent_vic is not None:
            self._goal_vic = self.bot._recent_vic
        # Also store it in the agent, if your agent logic uses self.bot._goal_vic / _goal_loc
        self.bot._goal_vic = self._goal_vic

        if self._goal_vic in self.bot._remaining:
            self._goal_loc = self.bot._remaining[self._goal_vic]
            self.bot._goal_loc = self._goal_loc

        # We switch the session phase to waiting for the human to come or to physically join
        self.currPhase = self.RedVictimPhase.WAITING_HUMAN
        self.ttl = ttl
        self.rescue_start_time = time.time()
        
        # Optionally: fetch the robot's location so we can do time/distance-based computations
        my_loc = None
        if "location" in self.bot.agent_properties and self.bot.agent_properties["location"] is not None:
            my_loc = self.bot.agent_properties["location"]  # e.g. (x,y)
        # or: my_loc = self.bot.state[self.bot.agent_id]['location'] if guaranteed in partial observation
        
        if my_loc:
            print("My current location:", my_loc)
            self.pickup_location = tuple(my_loc)
        
        print("Goal victim:", self._goal_vic)
        print("Goal location:", self._goal_loc)
        print("Pickup location:", self.pickup_location)

        # If you want to estimate delivery time from pickup to the goal:
        if self._goal_loc and self.pickup_location:
            self.estimated_delivery_time = self.estimate_delivery_time(
                self.pickup_location, self._goal_loc
            )
            print(f"Estimated delivery time: {self.estimated_delivery_time:.2f} seconds")

    def robot_continue_rescue(self):
        """User responded 'Continue' => they do NOT want to rescue the Red Victim now."""
        print("Robot Continue Rescue heard")
        # Decrease Willingness for ignoring the Red Victim
        self.increment_values("rescue_red", -0.15, 0, self.bot)
        # Then clean up
        self.delete_self()
    
    def wait(self):
        """
        Called each tick. 
        We simply decrement TTL and see if we time out.
        If still waiting for user or for them to show up, keep going. 
        If TTL hits 0 => on_timeout.
        """
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        # (Optionally) keep the session in sync with the agent's _recent_vic
        if self.bot._recent_vic and not self._goal_vic:
            self._goal_vic = self.bot._recent_vic
            self.bot._goal_vic = self._goal_vic

        # Copy from the agent's dictionary if missing
        if self._goal_vic and self._goal_loc is None:
            if self._goal_vic in self.bot._remaining and self.bot._remaining[self._goal_vic]:
                self._goal_loc = self.bot._remaining[self._goal_vic]
                self.bot._goal_loc = self._goal_loc

        # Store the door name for logs
        if self.bot._door['room_name'] and self.room_name is None:
            self.room_name = self.bot._door['room_name']
        
        # Decrement TTL
        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            return self.on_timeout()

        return 0

    def on_timeout(self):
        """If the user doesn't respond, or doesn't arrive, we skip rescue and penalize them."""
        if self.currPhase == self.RedVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for Red Victim decision!")
            self.increment_values("rescue_red", -0.2, -0.1, self.bot)

            self.bot._send_message(
                f"Skipping rescue of {self.bot._recent_vic} in {self.bot._door['room_name']} due to no response.", 
                "RescueBot"
            )
            self.bot._answered = True
            self.bot._waiting = False
            self.bot._rescue  = None 
            self.delete_self()
            return 1
        
        elif self.currPhase == self.RedVictimPhase.WAITING_HUMAN:
            # They said 'Rescue' but never showed up
            print("Timed out waiting for human to arrive! Human didn't show up!")
            self.increment_values("rescue_red", -0.1, -0.05, self.bot)

            self.bot._send_message(
                f"You did not show up to rescue {self.bot._recent_vic} in {self.room_name}; skipping.",
                "RescueBot"
            )
            self.bot._answered = True
            self.bot._waiting  = False
            self.bot._rescue   = None
            self.delete_self()
            return 1
        
        else:
            print("on_timeout called, but we are in an unknown phase—check logic!")
            return 1
        
    def human_showed_up(self):
        """
        If you detect the human arrived at the victim's location, or at least indicated readiness,
        you can finalize the rescue. 
        """
        print("Human showed up on time to rescue Red Victim together!")
        self.increment_values("rescue_red", 0.0, 0.1, self.bot)

    def complete_rescue_together(self):
        """
        Once the Red Victim is delivered, we finalize. 
        For example, we measure total rescue time vs. estimate, etc.
        """
        if self.rescue_start_time:
            total_time = time.time() - self.rescue_start_time
            print(f"Total rescue time: {total_time:.2f} seconds")
            # Possibly do advanced competence scaling if desired

        print("Completed rescue of Red Victim together!")
        self.increment_values("rescue_red", 0.1, 0.2, self.bot)
        self.delete_self()

    def delete_red_victim_session(self):
        print("Red Victim Session Deleted")
        self.bot._red_victim_session = None

    def estimate_delivery_time(self, start, end):
        """Example Manhattan distance -> approximate secs. Your logic may vary."""
        (x1, y1) = start
        (x2, y2) = end
        dist = abs(x1 - x2) + abs(y1 - y2)
        # Some scale factor, e.g. 1 second per tile
        return dist * 1.0
