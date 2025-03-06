from enum import Enum
import csv
import math
from pathlib import Path

class TrustBeliefs(Enum):
    SEARCH_WILLINGNESS = 1
    SEARCH_COMPETENCE = 2
    RESCUE_WILLINGNESS = 3
    RESCUE_COMPETENCE = 4
    REMOVE_WILLINGNESS = 5
    REMOVE_COMPETENCE = 6

class Baselines(Enum):
    ALWAYS_TRUST = 1
    NEVER_TRUST = -1
    ADAPTIVE = 0

class TrustService:
    HEADER = ['user_id'] + [belief.name.lower() for belief in TrustBeliefs]
    
    def __init__(self, baseline=Baselines.NEVER_TRUST):
        """
        Initializes the TrustService class.
        Attributes:
            csv_file (str): The path to the CSV file containing trust scores.
            trust_scores (dict): A dictionary to store trust scores.
            # Example of trust_scores:
            # {
            #     'user1': {
            #         TrustBeliefs.SEARCH_WILLINGNESS: 0.85,
            #         TrustBeliefs.SEARCH_COMPETENCE: 0.75,
            #         TrustBeliefs.RESCUE_WILLINGNESS: 0.65,
            #         TrustBeliefs.RESCUE_COMPETENCE: 0.55,
            #         TrustBeliefs.REMOVE_WILLINGNESS: 0.75,
            #         TrustBeliefs.REMOVE_COMPETENCE: 0.75
            #     },
            #     ...
            # }
        """
        
        self.baseline = baseline
        self.csv_file = Path('trust/trust_scores.csv')
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Perceived state represents the agent's understanding of the world.
        # perceived_state["rooms"] is a dictionary where keys are room IDs and values are dictionaries with room attributes.
        # Example:
        # perceived_state["rooms"]["room1"]["searched"] = 1 indicates that room1 has been searched by a human.
        # perceived_state["rooms"]["room1"]["searched"] = 2 indicates that room1 has been searched by a robot.
        self.perceived_state = {}
        
        self.trust_scores = {}

    def create_trust_file(self):
        if not self.csv_file.exists():
            with self.csv_file.open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADER)
            
    def load_trust_file(self):
        self.create_trust_file()
        with self.csv_file.open('r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                if self.baseline == Baselines.ADAPTIVE:
                    trust_score = {belief: float(row[belief.name.lower()]) for belief in TrustBeliefs}
                else:
                    trust_score = {belief: self.baseline.value for belief in TrustBeliefs}
                self.trust_scores[user_id] = trust_score
        
    def save_trust_file(self):
        self.create_trust_file()
        with self.csv_file.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADER)
            writer.writeheader()
            for user_id, score in self.trust_scores.items():
                row = {'user_id': user_id}
                row.update({belief.name.lower(): score[belief] for belief in TrustBeliefs})
                writer.writerow(row)

    def get_new_score_logarithmic(self, current_score, direction, weight, min_clamp = -1, max_clamp = 1):
        scaling_factor = (max_clamp - abs(current_score))  # Values closer to max get smaller updates

        log_weight = math.log1p(weight) * scaling_factor

        new_score = current_score + direction * log_weight

        # Clamp the new score between min and max
        new_score = max(min_clamp, min(max_clamp, new_score))

        return new_score
        
    def trigger_trust_change(self, trust_belief, user_id, send_message, value, weight=0.1, message=None):
        """
        Adjusts the trust score for a specific user and trust belief.

        Parameters:
            trust_belief (TrustBeliefs): The trust belief to update.
            user_id (str): The identifier of the user whose trust score will be adjusted.
            value (int): The direction of change (-1 or 1) indicating a decrease or increase.
            weight (float): A multiplier for how much the trust score should change.
        """
        if self.baseline != Baselines.ADAPTIVE:
            send_message("Trust is set to a baseline value, no change will be made.", 'DEBUG TRUST')
            return
        
        send_message("{} change triggered for user {} with value {} and weight {}".format(trust_belief, user_id, value, weight), 'DEBUG TRUST', True)
        if message:
            send_message("Message: {}".format(message), 'DEBUG TRUST')

        if user_id not in self.trust_scores:
            self.trust_scores[user_id] = {
                TrustBeliefs.SEARCH_WILLINGNESS: 0.0,
                TrustBeliefs.SEARCH_COMPETENCE: 0.0,
                TrustBeliefs.RESCUE_WILLINGNESS: 0.0,
                TrustBeliefs.RESCUE_COMPETENCE: 0.0,
                TrustBeliefs.REMOVE_WILLINGNESS: 0.0,
                TrustBeliefs.REMOVE_COMPETENCE: 0.0
            }

        # Retrieve the current score for the specified trust belief.
        current_score = self.trust_scores[user_id][trust_belief]
        new_score = self.get_new_score_logarithmic(current_score,value,weight)

        # Update the trust score.
        self.trust_scores[user_id][trust_belief] = new_score

        # Save the trust in a file
        self.save_trust_file() 

        print("DEBUG: Updated {} for user {}: {}".format(trust_belief.name, user_id, new_score))
            
    def human_search_room(self, room_id):
        """
        Marks a room as searched by a human.
        """
        if "rooms" not in self.perceived_state:
            self.perceived_state["rooms"] = {}
        if room_id not in self.perceived_state["rooms"]:
            self.perceived_state["rooms"][room_id] = {}
        if "searched" not in self.perceived_state["rooms"][room_id]:
            self.perceived_state["rooms"][room_id]["searched"] = 0
        self.perceived_state["rooms"][room_id]["searched"] = 1
        
    def robot_search_room(self, room_id):
        """
        Marks a room as searched by a robot.
        """
        if "rooms" not in self.perceived_state:
            self.perceived_state["rooms"] = {}
        if room_id not in self.perceived_state["rooms"]:
            self.perceived_state["rooms"][room_id] = {}
        if "searched" not in self.perceived_state["rooms"][room_id]:
            self.perceived_state["rooms"][room_id]["searched"] = 0
        self.perceived_state["rooms"][room_id]["searched"] = 2
        
    def was_searched(self, room_id):
        """
        Returns the integer value of the room's searched status.
        """
        if "rooms" not in self.perceived_state:
            return 0
        if room_id not in self.perceived_state["rooms"]:
            return 0
        if "searched" not in self.perceived_state["rooms"][room_id]:
            return 0
        return self.perceived_state["rooms"][room_id]["searched"]
    
    def add_victim(self, room_id, victim, found=1):
        """
        Adds a victim to the room.
        Parameters:
            room_id (str): The identifier of the room where the victim was found.
            victim (str): The identifier of the victim.
            found (int): The agent that found the victim (1 for human, 2 for robot).
        """
        if "rooms" not in self.perceived_state:
            self.perceived_state["rooms"] = {}
        if room_id not in self.perceived_state["rooms"]:
            self.perceived_state["rooms"][room_id] = {}
        if "victims" not in self.perceived_state["rooms"][room_id]:
            self.perceived_state["rooms"][room_id]["victims"] = []
        self.perceived_state["rooms"][room_id]["victims"].append({
            "victim": victim,
            "rescued": False,
            "found": 1
        })
        
    def victims(self, room_id, rescued=None, found=None):
        """
        Returns a list of victims in the room that meet the specified criteria.
        Parameters:
            room_id (str): The identifier of the room.
            rescued (bool): Whether the victim has been rescued.
            found (int): The agent that found the victim
        """
        if "rooms" not in self.perceived_state:
            return []
        if room_id not in self.perceived_state["rooms"]:
            return []
        if "victims" not in self.perceived_state["rooms"][room_id]:
            return []
        victims = self.perceived_state["rooms"][room_id]["victims"]
        if rescued is not None:
            victims = [v for v in victims if v["rescued"] == rescued]
        if found is not None:
            victims = [v for v in victims if v["found"] == found]
        return victims
        
    def update_victim(self, room_id, victim, rescued):
        """
        Updates the status of a victim in the room.
        Parameters:
            room_id (str): The identifier of the room where the victim was found.
            victim (str): The identifier of the victim.
            rescued (bool): Whether the victim has been rescued.
        """
        if "rooms" not in self.perceived_state:
            return
        if room_id not in self.perceived_state["rooms"]:
            return
        if "victims" not in self.perceived_state["rooms"][room_id]:
            return
        for v in self.perceived_state["rooms"][room_id]["victims"]:
            if v["victim"] == victim:
                v["rescued"] = rescued
                break
                
    # def add_victim(self, room_id, victim):
    #     """
    #     Adds a victim to the room.
    #     """
    #     if "rooms" not in self.perceived_state:
    #         self.perceived_state["rooms"] = {}
    #     if room_id not in self.perceived_state["rooms"]:
    #         self.perceived_state["rooms"][room_id] = {}
    #     if "victims" not in self.perceived_state["rooms"][room_id]:
    #         self.perceived_state["rooms"][room_id]["victims"] = []
    #     self.perceived_state["rooms"][room_id]["victims"].append(victim)