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
    VERY_LOW_WILLINGNESS_THRESHOLD = -0.5
    
    COMPETENCE_THRESHOLD = 0.0
    VERY_LOW_COMPETENCE_THRESHOLD = -0.5
    
    
    
    def __init__(self, bot, info, ttl=-1):
        super().__init__(bot, info, ttl)
        self.currPhase = self.YellowVictimPhase.WAITING_RESPONSE
        
        self._goal_vic = None
        self._goal_loc = None
        
        self.recent_vic = None
        self.room_name = None



    # Factors to adjust Competence and Willingness
    # Robot found a yellow victim
    def robot_continue_rescue(self, number_of_actions = 0, use_confidence = False):
        print("Robot Continue Rescue heard")
        
        increment_value = -0.1   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
        
        self.increment_values("rescue_yellow", increment_value, 0, self.bot)
        self.delete_self()
        
    def robot_rescue_alone(self, number_of_actions = 0, use_confidence = False):
        print("Robot Rescue Alone heard")
        
        increment_value = 0.1   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", increment_value, 0, self.bot)
        self.delete_self()

    def robot_rescue_together(self, ttl=50, number_of_actions = 0, use_confidence = False):
        print("Robot Rescue Together heard")
        
        increment_value = 0.15   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", increment_value, 0, self.bot)
        # Wait for the human
        self.currPhase = self.YellowVictimPhase.WAITING_HUMAN
        # Reset ttl
        self.ttl = ttl
  
    
    def human_showed_up(self, number_of_actions = 0, use_confidence = False):
        print("Human showed up on time to rescue Yellow Victim together")
        
        increment_value = 0.1   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", 0.0, increment_value, self.bot)
    
    
    # Human found a yellow victim       
    def human_found_alone_truth(self, number_of_actions = 0, use_confidence = False):
        print("Human claimed to have Found a new Yellow Victim")
        
        increment_value = 0.1   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", increment_value, 0.0, self.bot)
    
    def human_found_alone_lie(self, number_of_actions = 0, use_confidence = False):
        print("Human claimed to have Found a new Yellow Victim, while this victim has been Found before")
        
        increment_value = -0.15   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", increment_value, 0.0, self.bot)
    
    
    def human_collect_alone_truth(self, number_of_actions = 0, use_confidence = False):
        # higher competencec than human_rescue_together, because he can pickup alone
        print("Human claimed to have Collected a new Yellow Victim")
        
        increment_value = 0.1   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", 0.0, increment_value, self.bot)
    
    def human_collect_alone_lie(self, number_of_actions = 0, use_confidence = False):
        print("Human claimed to have Collected a new Yellow Victim, while this victim has been Collected before")
        
        increment_value = -0.15   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", 0.0, increment_value, self.bot)
    
    def human_collect_alone_lie_location(self, number_of_actions = 0, use_confidence = False):
        print("Human claimed to have Collected a new Yellow Victim, while this victim has been (claimed to be) found elsewhere")
        
        increment_value = -0.05   
        if use_confidence:
            increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
        self.increment_values("rescue_yellow", 0.0, increment_value, self.bot)    
    
    
    def human_rescue_together(self, number_of_actions = 0, use_confidence = False):
        pass
        

    # def complete_rescue_together(self, number_of_actions, use_confidence = False):
    #     print("Completed rescue!")
            
    #     self.increment_values("rescue_yellow", 0.1, 0.2, self.bot)
    #     self.delete_self()
            
    
    # Determine which decision the agent should make based on trust values
    def decision_making(self):
        competence = self.bot._trustBeliefs[self.bot._human_name]['rescue_yellow']['competence']
        willingness = self.bot._trustBeliefs[self.bot._human_name]['rescue_yellow']['willingness']
        
        print(f"competence: {competence}")
        print(f"willingness: {willingness}")

        if willingness < self.VERY_LOW_WILLINGNESS_THRESHOLD or competence < self.VERY_LOW_COMPETENCE_THRESHOLD:
            return self.TrustDecision.LOW_COMPETENCE_AND_LOW_WILLINGNESS
        
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
          
    
    def delete_yellow_victim_session(self, flag=True):
        self.bot._yellow_victim_session = None
        if flag:
            print("Yellow Victim Session Deleted")
    
    
    def wait(self, number_of_actions = 0, use_confidence = False):
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
            return self.on_timeout(number_of_actions, use_confidence)
            
        ####
        return 0
       

    def on_timeout(self, number_of_actions = 0, use_confidence = False):
        # Figure out what to do depending on the current phase
        if self.currPhase == self.YellowVictimPhase.WAITING_RESPONSE:
            print("Timed out waiting for response!")
            
            increment_value = -0.10   
            if use_confidence:
                increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
            
            self.increment_values("rescue_yellow", increment_value, 0.0, self.bot)

            from agents1.OfficialAgent import Phase
            self.bot._send_message('Picking up ' + self.bot._recent_vic + ' in ' + self.bot._door['room_name'] + '.',
                                'RescueBot')
            self.bot._rescue = 'alone'
            
            # Change to True if this causes issues:
            self.bot._answered = True
            
            self.bot._waiting = False
            self.bot._goal_vic = self.bot._recent_vic
            self.bot._goal_loc = self.bot._remaining[self.bot._goal_vic]
            self.bot._recent_vic = None
            self.bot._phase = Phase.PLAN_PATH_TO_VICTIM
           
            self.delete_yellow_victim_session()
            
            #####
            return 1
                    
        elif self.currPhase == self.YellowVictimPhase.WAITING_HUMAN:
            print("Timed out waiting for human! Human Didn't show up!")
            
            increment_value = -0.10   
            if use_confidence:
                increment_value = self.calculate_increment_with_confidence(number_of_actions, increment_value)
                
            self.increment_values("rescue_yellow", 0.0, increment_value, self.bot)

            from agents1.OfficialAgent import Phase
            
            self.bot._rescue = 'alone'
            
            self.bot._send_message('Picking up ' + self.recent_vic + ' in ' + self.room_name + '.',
                                'RescueBot')
                
            # Change to True if this causes issues:
            self.bot._answered = True
            
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

