import enum
from agents1.eventUtils import PromptSession

class RockObstacleSession(PromptSession):
    count_actions = 0

    class RockObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    def __init__(self, bot, info, ttl=100):
        super().__init__(bot, info, ttl)
        self.currPhase = self.RockObstaclePhase.WAITING_RESPONSE
        self.removal_time = 50
        self.removal_in_progress = False

    def continue_rock(self):
        """
        Called when the human chooses to ignore or skip removing the big rock.
        Reduces willingness for 'remove_rock'.
        """
        print("Continue Rock heard")
        self.increment_values("remove_rock", -0.1, 0, self.bot)
        self.delete_self()

    def remove_rock(self):
        """
        Called when the human is willing to remove the big rock. 
        We slightly increase willingness. 
        """
        print("Remove Rock heard")
        self.increment_values("remove_rock", 0.1, 0, self.bot)
        self.currPhase = self.RockObstaclePhase.WAITING_HUMAN
        self.ttl = 100

    def complete_remove_rock(self):
        print("Completed big rock removal!")
        self.increment_values("remove_rock", 0.05, 0.1, self.bot)
        
        from agents1.OfficialAgent import RemoveObject, Phase
        # Make sure to set these so the agent knows we’re done
        self.bot._answered = True
        self.bot._waiting = False
        self.bot._remove = False
        self.bot._phase = Phase.ENTER_ROOM

        # Remove the session from the bot
        self.delete_self()
        
        # **Return the actual remove action** so MATRX removes the object
        return RemoveObject.__name__, {'object_id': self.info['obj_id']}

    def on_timeout(self):
        """
        If the user fails to respond or arrive within 'ttl' ticks, skip the obstacle.
        """
        print("Timed out waiting for response or for human to arrive!")
        # Adjust trust as you like:
        if self.currPhase == self.RockObstaclePhase.WAITING_RESPONSE:
            self.increment_values("remove_rock", -0.15, -0.15, self.bot)
            self.bot._send_message(
                "No response about removing the big rock. I will skip it and continue searching.",
                "RescueBot"
            )
        elif self.currPhase == self.RockObstaclePhase.WAITING_HUMAN:
            self.increment_values("remove_rock", -0.1, -0.1, self.bot)
            self.bot._send_message(
                "We agreed to remove the big rock together, but nobody arrived. I will skip it and continue.",
                "RescueBot"
            )

        self.bot._skipped_obstacles.append(self.info['obj_id'])
        
        return self._finish_session()

    def wait(self):
        """
        Override the default wait method to check for human arrival.
        Returns None, {} to maintain idle state.
        """
        if self.currPhase == self.RockObstaclePhase.WAITING_HUMAN:
            # Check if human has arrived
            state = self.bot.state
            if state and state[{'is_human_agent': True}]:
                if not self.removal_in_progress:
                    # Human just arrived, start the removal process
                    self.bot._send_message('Removing the big rock blocking ' + str(self.bot._door['room_name']) + ' together!', 'RescueBot')
                    self.removal_in_progress = True
                    
                # Count down the removal time
                if self.removal_in_progress:
                    self.removal_time -= 1
                    if self.removal_time <= 0:
                        # Removal process is complete
                        return self.complete_remove_rock()
        
        # Either waiting for response or human hasn't arrived yet or removal in progress
        self.ttl -= 1
        if self.ttl <= 0 and not self.removal_in_progress:
            return self.on_timeout()
        return None, {}

    def _finish_session(self):
        """ Helper to finish the session, set the agent to proceed with searching. """
        from agents1.OfficialAgent import Phase
        from actions1.CustomActions import Idle
        # Switch agent to searching
        self.bot._answered = True
        self.bot._waiting = False
        self.bot._remove = False
        self.bot._phase = Phase.FIND_NEXT_GOAL

        # Actually remove the session from the agent
        self.delete_self()

        # Return a 1-tick Idle to break out. Next tick, the agent will do normal searching.
        return Idle.__name__, {}

    @staticmethod
    def increment_values(task, willingness, competence, bot):
        RockObstacleSession.count_actions += 1
        print("Confidence:", RockObstacleSession.get_confidence())
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness",
                         RockObstacleSession.get_confidence() * willingness)
        bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence",
                         RockObstacleSession.get_confidence() * competence)

    @staticmethod
    def get_confidence():
        return min(1.0, max(0.0, RockObstacleSession.count_actions / 2))
