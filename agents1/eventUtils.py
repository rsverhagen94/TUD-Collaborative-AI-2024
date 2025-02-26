import enum

from agents1.OfficialAgent import BaselineAgent

# Is this a good idea, having this definition outside the class scope?
default_timer = 100

class RemoveObstacleEvents:
    @staticmethod
    def removeStoneTogether(bot):
        print("Remove Stone Together heard")
        # Make the bot wait
        bot._ticks_waiting = default_timer
        # Udpate Values
        RemoveObstacleEvents.increment_values("remove_stone", 0.1, 0, bot)
        bot._waiting_human = True

    @staticmethod
    def removeStoneAlone(bot):
        print("Remove Stone Alone heard")
        RemoveObstacleEvents.increment_values("remove_stone", 0.1, 0, bot)

    @staticmethod
    def continueStoneEvent(bot):
        print("Continue Stone heard")
        RemoveObstacleEvents.increment_values("remove_stone", -0.1, 0, bot)

    @staticmethod
    def waitStoneEvent(bot):
        print("Wait Stone triggered, ticks waiting", bot._ticks_waiting)
        # TODO: how do we know which event we are waiting for? Ans: The bot will only wait in the case of Remove Together

        if bot._waiting_human:
            # A timeout has happened
            if bot._ticks_waiting <= 0:
                bot._ticks_waiting = 0 # Clip ticks_waiting to prevent errors
                print("Timeout!")
                RemoveObstacleEvents.increment_values("remove_stone", -0.1, 0, bot)
            else:
                print("waiting")
                bot._ticks_waiting -= 1

    @staticmethod
    def completeRemoveTogetherEvent(bot):
        if bot._waiting_human:
            bot._ticks_waiting = 0
            bot._waiting_human = False
            RemoveObstacleEvents.increment_values("remove_stone", 0.2, 0.1, bot)
            print("Remove stone together completed, adding")


    @staticmethod
    def increment_values(task, willingness, competence, bot):
        # TODO: implement this later
        # bot._willingness += willingness
        # bot._competence += competence
        pass


