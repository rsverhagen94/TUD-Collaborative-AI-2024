import enum
from agents1.eventUtils import PromptSession


class YellowVictimSession(PromptSession):
    class YellowVictimPhase(enum.Enum):
        WAITING_RESPONSE = 0
        WAITING_HUMAN = 1

    class TrustDecision(enum.Enum):
        LOW_COMPETENCE_AND_LOW_WILLINGNESS = 0
        HIGH_WILLINGNESS_OR_HIGH_COMPETENCE = 1
        HIGH_COMPETENCE_AND_HIGH_WILLINGNESS = 2
    
    # Trust Belief Thresholds
    WILLINGNESS_THRESHOLD = 0.7
    COMPETENCE_THRESHOLD = 0.7
    
    
    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.YellowVictimPhase.WAITING_RESPONSE
        
        self._goal_vic = None
        self._goal_loc = None
        
        self.recent_vic = None
        self.room_name = None

    # Factors to adjust Competence and Willingness
    # Robot found a yellow victim
    def robot_continue_rescue(self):
        print("Robot Continue Rescue heard")
        self.increment_values("rescue_yellow", -0.1, 0, self.bot)
        self.delete_self()
        
    def robot_rescue_alone(self):
        print("Robot Rescue Alone heard")
        self.increment_values("rescue_yellow", 0.1, 0, self.bot)
        self.delete_self()

    def robot_rescue_together(self, ttl=20):
        print("Robot Rescue Together heard")
        self.increment_values("rescue_yellow", 0.15, 0, self.bot)
        # Wait for the human
        self.currPhase = self.YellowVictimPhase.WAITING_HUMAN
        # Reset ttl
        self.ttl = ttl
  
    # Human found a yellow victim       
    def human_found_alone(self):
        pass
    def human_rescue_alone(self):
        # higher competencec than below, because he can pickup alone
        pass
    def human_rescue_together(self):
        pass
        

    def complete_rescue_together(self):
        print("Completed rescue!")
        self.increment_values("rescue_yellow", 0.1, 0.2, self.bot)
        self.delete_self()
            
    # Determine which decision the agent should make based on trust values
    def decision_making(self):
        competence = self.bot._trustBeliefs[self.bot._human_name]['rescue_yellow']['competence']
        willingness = self.bot._trustBeliefs[self.bot._human_name]['rescue_yellow']['willingness']
        
        print(f"competence: {competence}")
        print(f"willingness: {willingness}")

        if willingness < self.WILLINGNESS_THRESHOLD and competence < self.COMPETENCE_THRESHOLD:
            return self.TrustDecision.LOW_COMPETENCE_AND_LOW_WILLINGNESS
        
        if willingness >= self.WILLINGNESS_THRESHOLD and competence >= self.COMPETENCE_THRESHOLD:
            return self.TrustDecision.HIGH_COMPETENCE_AND_HIGH_WILLINGNESS
        
        return self.TrustDecision.HIGH_WILLINGNESS_OR_HIGH_COMPETENCE
        
    
    def decision_to_rescue(self):
        if self.bot._door['room_name'] not in self.bot._searched_rooms:
            self.bot._searched_rooms.append(self.bot._door['room_name'])
        
        from agents1.OfficialAgent import Phase
        
        self.bot._send_message('Picking up ' + self.bot._recent_vic + ' in ' + self.bot._door['room_name'] + '.', 'RescueBot')
        self.bot._rescue = 'alone'
        self.bot._answered = True
        self.bot._waiting = False
        
        self.bot._goal_vic = self.bot._recent_vic
        self.bot._goal_loc = self.bot._remaining[self.bot._goal_vic]
        self.bot._recent_vic = None
        
        self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
        
        self.delete_yellow_victim_session()
        
        return None, {}
    
    def decision_to_continue(self):
        if self.bot._door['room_name'] not in self.bot._searched_rooms:
            self.bot._searched_rooms.append(self.bot._door['room_name'])
        
        from agents1.OfficialAgent import Phase
        
        self.bot._answered = True
        self.bot._waiting = False
        self.bot._todo.append(self.bot._recent_vic)
        self.bot._recent_vic = None
        
        self.bot._phase = Phase.FIND_NEXT_GOAL
        
        self.delete_yellow_victim_session()

        return None, {} 
          
    
    def delete_yellow_victim_session(self):
        self.bot._yellow_victim_session = None
        print("Yellow Victim Session Deleted")
    
    
    def wait(self):
        if self.ttl % 5 == 0 and self.ttl > 0:
            print("ttl:", self.ttl)

        if self.bot._recent_vic is not None and self._goal_vic is None:
            self._goal_vic = self.bot._recent_vic
        
        if self.bot._goal_vic is not None and self.bot._goal_vic in self.bot._remaining:
            if self.bot._remaining[self.bot._goal_vic] is not None and self._goal_loc is None:
                self._goal_loc = self.bot._remaining[self.bot._goal_vic]
                
        if self.bot._recent_vic is not None and self.recent_vic is None:
            self.recent_vic = self.bot._recent_vic
            
        if self.bot._door['room_name'] is not None and self.room_name is None:
            self.room_name = self.bot._door['room_name']
        
        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            return self.on_timeout()
            
        ####
        return 0   

    def on_timeout(self):
        # Figure out what to do depending on the current phase
        if self.currPhase == self.YellowVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for response!")
            self.increment_values("rescue_yellow", -0.15, -0.15, self.bot)

            from agents1.OfficialAgent import Phase
            self.bot._send_message('Picking up ' + self.bot._recent_vic + ' in ' + self.bot._door['room_name'] + '.',
                                'RescueBot')
            self.bot._rescue = 'alone'
            
            # Change to True if this causes issues:
            self.bot._answered = True
            #
            
            self.bot._waiting = False
            self.bot._goal_vic = self.bot._recent_vic
            self.bot._goal_loc = self.bot._remaining[self.bot._goal_vic]
            self.bot._recent_vic = None
            self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
           
            self.delete_yellow_victim_session()
            
            #####
            return 1
                    
        elif self.currPhase == self.YellowVictimPhase.WAITING_HUMAN:
            print("Timed out waiting for human!")
            self.increment_values("rescue_yellow", -0.1, 0, self.bot)

            from agents1.OfficialAgent import Phase
            
            self.bot._rescue = 'alone'
            
            self.bot._send_message('Picking up ' + self.recent_vic + ' in ' + self.room_name + '.',
                                'RescueBot')
                
            # Change to True if this causes issues:
            self.bot._answered = True
            # 
            
            self.bot._waiting = False
            self.bot._goal_vic = self._goal_vic
            self.bot._goal_loc = self._goal_loc
            self.bot._recent_vic = None
            
            self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
            
            self.delete_yellow_victim_session()
            
            ####
            return 1


        else:
            print("How did you even get here?!")
            pass

#TODO: Implement Confidence Level