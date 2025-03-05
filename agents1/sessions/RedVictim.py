import enum, time, math
from agents1.eventUtils import PromptSession

class RedVictimSession(PromptSession):
    class RedVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1
        IN_PROGRESS = 2

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

    @staticmethod
    def calculate_time_proximity_scale(actual_time, estimated_time, max_deviation=20):
        """
        Calculate a scaling factor (0..1) based on how close actual time is to the estimated time.
        Large deviations lead to lower scaling; small deviations closer to 1.
        """
        time_diff = abs(actual_time - estimated_time)
        if time_diff <= max_deviation:
            # Logarithmic scaling to weight small deviations more strongly
            return 1 - math.log(time_diff + 1) / math.log(max_deviation + 1)
        else:
            # If it’s far beyond the acceptable deviation, we return a negative signal
            return -1

    def modify_competence_by_time(self, actual_time, estimated_time):
        """
        Modify competence (and optionally willingness) based on how close
        the actual time is to the estimated rescue-delivery time.
        """
        time_scale = self.calculate_time_proximity_scale(actual_time, estimated_time)
        if time_scale >= 0:
            competence_change = 0.1 * time_scale
            willingness_change = 0.05 * time_scale
            self.increment_values("rescue_red", willingness_change, competence_change, self.bot)
        else:
            # If user is significantly late or large mismatch, we lower trust
            self.increment_values("rescue_red", -0.05, -0.1, self.bot)

    def robot_rescue_together(self, ttl=100):
        """
        Called when the user/robot decided to rescue a critically injured Red Victim together.
        We set the session phase to WAITING_HUMAN with a short TTL (e.g. 10s).
        """
        print("Robot Rescue Together heard.")
        self.increment_values("rescue_red", 0.15, 0, self.bot)  # Slight willingness bump

        # Identify the victim we’re rescuing
        if self.bot._recent_vic is not None:
            self._goal_vic = self.bot._recent_vic
        self.bot._goal_vic = self._goal_vic

        # Identify location
        if self._goal_vic in self.bot._remaining:
            self._goal_loc = self.bot._remaining[self._goal_vic]
            self.bot._goal_loc = self._goal_loc

        # Transition to WAITING_HUMAN
        self.currPhase = self.RedVictimPhase.WAITING_HUMAN
        self.ttl = ttl
        self.rescue_start_time = time.time()

        # Optionally store the robot’s current location for an ETA calculation
        my_loc = None
        if "location" in self.bot.agent_properties and self.bot.agent_properties["location"] is not None:
            my_loc = self.bot.agent_properties["location"]  # (x, y)

        if my_loc:
            self.pickup_location = tuple(my_loc)

        # Optionally estimate time
        if self._goal_loc and self.pickup_location:
            self.estimated_delivery_time = self.estimate_delivery_time(self.pickup_location, self._goal_loc)
            print(f"Estimated delivery time: {self.estimated_delivery_time:.2f} seconds")

        print(f"Goal victim: {self._goal_vic}")
        print(f"Goal location: {self._goal_loc}")
        print(f"Pickup location: {self.pickup_location}")

    def robot_continue_rescue(self):
        """
        Called if the user or the agent decided to skip or 'continue searching' 
        (i.e., not rescue this red victim now).
        """
        print("Robot Continue Rescue heard.")
        # Slight penalty for ignoring a red victim
        self.increment_values("rescue_red", -0.15, 0, self.bot)
        # Clean up
        self.delete_self()
    
    def wait(self):
        """
        Called each tick to decrement TTL and handle transitions.
        """
        if self.ttl > 0:
            self.ttl -= 1

        # If we timed out before the user responded or arrived
        if self.ttl == 0:
            return self.on_timeout()

        # If we are waiting for the human physically
        if self.currPhase == self.RedVictimPhase.WAITING_HUMAN:
            if self.check_human_proximity():
                self.human_showed_up()
                # Once we do that, we won't keep printing "Human showed up..."
                self.currPhase = self.RedVictimPhase.IN_PROGRESS
                # Also, we might want to set ttl = -1 so it no longer times out
                self.ttl = -1  
                return 0

        return 0

    def on_timeout(self):
        """Handle session timeout for both WAITING_RESPONSE and WAITING_HUMAN."""
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
            # They said "Yes, let's rescue," but never arrived
            print("Timed out waiting for human to arrive! Human did not show up in time.")
            self.increment_values("rescue_red", -0.1, -0.05, self.bot)

            self.bot._send_message(
                f"You did not show up to rescue {self._goal_vic} in {self.room_name}. Skipping!",
                "RescueBot"
            )
            # Let the agent continue searching, ignoring this victim
            self.bot._answered = True
            self.bot._waiting = False
            self.bot._rescue  = None
            self.delete_self()
            return 1

        else:
            print("on_timeout called, but we are in an unknown phase—no action taken.")
            return 1
        
    def check_human_proximity(self, threshold=1):
        """
        Checks if the human is in proximity of the robot or the victim's location.
        If the environment state is partial, adapt accordingly.
        
        Return True if the human is 'close enough' to proceed, otherwise False.
        """
        state = self.bot.state  # However you access environment data
        human_location = None
        robot_location = None

        # Find the human’s location
        for obj_id, info in state.items():
            if info.get('is_human_agent') == True:
                human_location = info.get('location')
            if obj_id == self.bot.agent_id:  # or whichever entry indicates the robot
                robot_location = info.get('location')

        if human_location and robot_location:
            dist = abs(human_location[0] - robot_location[0]) + abs(human_location[1] - robot_location[1])
            return dist <= threshold

        return False
        
    def human_showed_up(self):
        """
        Called once the session detects the human arrived in proximity.
        """
        print("Human showed up on time to rescue Red Victim together!")
        self.increment_values("rescue_red", 0.0, 0.1, self.bot)


    def complete_rescue_together(self):
        """
        Called once the red victim is actually dropped off at the drop zone.
        We optionally factor in how quickly we completed the rescue 
        (vs. an estimated_delivery_time).
        """
        if self.rescue_start_time:
            total_time = time.time() - self.rescue_start_time
            if self.estimated_delivery_time:
                # Modify competence by how close actual time was to the estimate
                self.modify_competence_by_time(total_time, self.estimated_delivery_time)
            print(f"Total rescue time for Red Victim: {total_time:.2f} seconds")

        print("Completed rescue of Red Victim together!")
        # Increase willingness & competence further now that the rescue is done
        self.increment_values("rescue_red", 0.1, 0.2, self.bot)
        self.delete_self()

    def delete_red_victim_session(self):
        """
        Manually delete this session if you want from outside code.
        """
        print("Red Victim Session Deleted")
        self.bot._red_victim_session = None

    def estimate_delivery_time(self, start, end):
        """
        A simple Manhattan-distance-based guess for how many seconds
        a pickup + drop might take. Tweak as necessary.
        """
        (x1, y1) = start
        (x2, y2) = end
        dist = abs(x1 - x2) + abs(y1 - y2)
        # Some scale factor, e.g. 1 second per tile
        return dist * 1.0
