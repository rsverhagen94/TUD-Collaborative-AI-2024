import enum
from abc import abstractmethod


class Scenario(enum.Enum):
    USE_TRUST_MECHANISM = 0
    ALWAYS_TRUST = 1
    NEVER_TRUST = 2
    RANDOM_TRUST = 3


# Class to manage which prompt was last encountered by the bot
class PromptSession:
    # Shared variable across all instances of PromptSession
    scenario_used = Scenario.USE_TRUST_MECHANISM

    def __init__(self, bot, info, ttl=100):
        self.bot = bot
        self.info = info  # Store info about the current object (used for directing removal)
        self.ttl = ttl  # How long the prompt should wait for a response (not wait for a human to show up!)

    def wait(self):
        # Updates the ttl of the prompt every time it is called
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            # Direct the bot to perform an action if the prompt's time to live has expired
            return self.on_timeout()

        # Do nothing if the prompt still has time to live
        return None, {}

    @abstractmethod
    def on_timeout(self): pass

    def delete_self(self):
        self.bot._current_prompt = None

    @staticmethod
    def increment_values(task, willingness, competence, bot):
        # Update trust beliefs for a particular task by defined increments
        if PromptSession.scenario_used == Scenario.USE_TRUST_MECHANISM:
            bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "willingness", willingness)
            bot._trustBelief(bot._team_members, bot._trustBeliefs, bot._folder, task, "competence", competence)
        
        
    def calculate_increment_with_confidence(self, number_of_actions, base_increment, confidence_constant=250):
        """
        Adjust the increment based on confidence.
        Formula: (1 - confidence) * base_increment
        
        The logic behind this: Looking through the POV of the current Willingness and Competence values,
        - Low confidence => You have low confidence in these values at the moment, so you will allow for large magnitude updates (the returned increment)
        - High confidence => You have high confidence in these values at the moment, so you won't allow for large magnitude updates (the returned increment)
        """
        confidence = self.calculate_confidence(number_of_actions, confidence_constant)
        return (1 - confidence) * base_increment
    
    def calculate_confidence(self, number_of_actions, constant):
        """
        Calculate confidence as a ratio of actions performed to a given constant.
        Ensures the value remains between 0 and 1.
        """
        return min(1.0, max(0.0, number_of_actions / constant))