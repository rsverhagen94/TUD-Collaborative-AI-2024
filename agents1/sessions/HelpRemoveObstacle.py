import enum, time, math
from agents1.eventUtils import PromptSession

class HelpRemoveObstacleSession(PromptSession):
    class HelpRemoveObstaclePhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1
        
     


    