import enum
from agents1.eventUtils import PromptSession


class YellowVictimSession(PromptSession):
    class YellowVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, ttl=-1):
        super().__init__(bot, ttl)
        self.currPhase = self.YellowVictimPhase.WAITING_RESPONSE

    def robot_continue_rescue(self):
        print("Robot Continue Rescue heard")
        self.increment_values("rescue_yellow", -0.1, 0, self.bot)
        self.delete_self()
        
    def robot_rescue_alone(self):
        print("Robot Rescue Alone heard")
        self.increment_values("rescue_yellow", 0.1, 0, self.bot)
        self.delete_self()

    def robot_remove_together(self, ttl=100):
        print("Robot Rescue Together heard")
        self.increment_values("rescue_yellow", 0.15, 0, self.bot)
        # Wait for the human
        self.currPhase = self.YellowVictimPhase.WAITING_HUMAN
        # Reset ttl
        self.ttl = ttl
        
        
    def human_found_alone(self):
        pass
    def human_pickup_alone(self):
        # higher competencec than below, because he can pickup alone
        pass
    def human_pickup_together(self):
        pass
        
    
        

    def complete_rescue_together(self):
        print("Completed rescue!")
        self.increment_values("rescue_yellow", 0.1, 0.2, self.bot)
        self.delete_self()

    def wait(self):
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            self.on_timeout()

    def on_timeout(self):
        # Figure out what to do depending on the current phase
        if self.currPhase == self.YellowVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for response!")
            self.increment_values("rescue_yellow", -0.15, -0.15, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            # Add area to the to do list
            self.bot._to_search.append(self.bot._door['room_name'])

            from agents1.OfficialAgent import Phase
            self.bot._phase = Phase.FIND_NEXT_GOAL
            self.delete_self()

        elif self.currPhase == self.YellowVictimPhase.WAITING_HUMAN:
            print("Timed out waiting for human!")
            self.increment_values("rescue_yellow", -0.1, 0, self.bot)

            self.bot._answered = True
            self.bot._waiting = False
            # Add area to the to do list
            self.bot._to_search.append(self.bot._door['room_name'])

            from agents1.OfficialAgent import Phase
            self.bot._phase = Phase.FIND_NEXT_GOAL
            self.delete_self()


        else:
            print("How did you even get here?!")
            pass

#TODO: Implement Confidence Level