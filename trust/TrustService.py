from enum import Enum
import os
import csv

class TrustBeliefs(Enum):
    SEARCH_WILLINGNESS = 1
    SEARCH_COMPETENCE = 2
    RESCUE_WILLINGNESS = 3
    RESCUE_COMPETENCE = 4
    REMOVE_WILLINGNESS = 5
    REMOVE_COMPETENCE = 6

class TrustService:
    
    def __init__(self):
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
        
        self.csv_file = 'trust/trust_scores.csv'
        self.trust_scores = {}
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        
        # Perceived state represents the agent's understanding of the world.
        # perceived_state["rooms"] is a dictionary where keys are room IDs and values are dictionaries with room attributes.
        # Example:
        # perceived_state["rooms"]["room1"]["searched"] = 1 indicates that room1 has been searched by a human.
        # perceived_state["rooms"]["room1"]["searched"] = 2 indicates that room1 has been searched by a robot.
        self.perceived_state = {}

    def create_trust_file(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'user_id',
                    'search_willingness',
                    'search_competence',
                    'rescue_willingness',
                    'rescue_competence',
                    'remove_willingness',
                    'remove_competence'
                ])
            
    def load_trust_file(self):
        if not os.path.exists(self.csv_file):
            self.create_trust_file()
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                trust_score = {
                    TrustBeliefs.SEARCH_WILLINGNESS: float(row['search_willingness']),
                    TrustBeliefs.SEARCH_COMPETENCE: float(row['search_competence']),
                    TrustBeliefs.RESCUE_WILLINGNESS: float(row['rescue_willingness']),
                    TrustBeliefs.RESCUE_COMPETENCE: float(row['rescue_competence']),
                    TrustBeliefs.REMOVE_WILLINGNESS: float(row['remove_willingness']),
                    TrustBeliefs.REMOVE_COMPETENCE: float(row['remove_competence'])
                }
                self.trust_scores[user_id] = trust_score
        
    def save_trust_file(self):
        if not os.path.exists(self.csv_file):
            self.create_trust_file()
        # Write the combined data back to the file.
        with open(self.csv_file, 'w', newline='') as f:
            fieldnames = [
                'user_id',
                'search_willingness',
                'search_competence',
                'rescue_willingness',
                'rescue_competence',
                'remove_willingness',
                'remove_competence'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user_id, score in existing_scores.items():
                writer.writerow({
                    'user_id': user_id,
                    'search_willingness': score[TrustBeliefs.SEARCH_WILLINGNESS],
                    'search_competence': score[TrustBeliefs.SEARCH_COMPETENCE],
                    'rescue_willingness': score[TrustBeliefs.RESCUE_WILLINGNESS],
                    'rescue_competence': score[TrustBeliefs.RESCUE_COMPETENCE],
                    'remove_willingness': score[TrustBeliefs.REMOVE_WILLINGNESS],
                    'remove_competence': score[TrustBeliefs.REMOVE_COMPETENCE]
                })
        
    def trigger_trust_change(self, trust_belief, user_id, send_message, value, weight=1, message=None):
        """
        Adjusts the trust score for a specific user and trust belief.

        Parameters:
            trust_belief (TrustBeliefs): The trust belief to update.
            user_id (str): The identifier of the user whose trust score will be adjusted.
            value (int): The direction of change (-1 or 1) indicating a decrease or increase.
            weight (float): A multiplier for how much the trust score should change.
        """
        send_message("Trust belief change triggered for user {} with value {} and weight {}".format(user_id, value, weight), 'DEBUG TRUST', True)
        if message:
            send_message("Message: {}".format(message), 'DEBUG TRUST')
            
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