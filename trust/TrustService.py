from enum import Enum
import csv
import math
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

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
    
    def __init__(self, baseline=Baselines.ADAPTIVE):
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

        self.evolution_folder = self.csv_file.parent / "evolution"
        self.evolution_folder.mkdir(parents=True, exist_ok=True)
        self.game_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.evolution_file = self.evolution_folder / f"trust_evolution_{self.game_timestamp}.csv"
    
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
        plot_users = ["Ben", "Charlie", "Alice"]
        with self.csv_file.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADER)
            writer.writeheader()
            for user_id, score in self.trust_scores.items():
                row = {'user_id': user_id}
                row.update({belief.name.lower(): score[belief] for belief in TrustBeliefs})
                writer.writerow(row)
                
        for user in plot_users:
            self.plot_trust_evolution(user)

    def get_new_score_logarithmic(self, current_score, direction, weight, min_clamp=-1, max_clamp=1):
        scaling_factor = (max_clamp - abs(current_score))
        log_weight = math.log1p(weight) * scaling_factor
        new_score = current_score + direction * log_weight
        return max(min_clamp, min(max_clamp, new_score))
        
    def log_trust_change(self, user_id, trust_belief, old_score, new_score, direction, weight, message):
        timestamp = datetime.now().isoformat()
        file_exists = self.evolution_file.exists()
        with self.evolution_file.open('a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'user_id', 'trust_belief', 'old_score', 'new_score', 'change_direction', 'weight', 'message'])
            writer.writerow([timestamp, user_id, trust_belief.name, old_score, new_score, direction, weight, message if message else ""])
    
    def trigger_trust_change(self, trust_belief, user_id, send_message, value, weight=0.1, message=None):
        """
        Adjusts the trust score for a specific user and trust belief, and logs the evolution.
        """
        if self.baseline != Baselines.ADAPTIVE:
            send_message("Trust is set to a baseline value, no change will be made.", 'DEBUG TRUST')
            return
        
        send_message(f"{trust_belief} change triggered for user {user_id} with value {value} and weight {weight}", 'DEBUG TRUST', True)
        if message:
            send_message(f"Message: {message}", 'DEBUG TRUST')
        
        if user_id not in self.trust_scores:
            self.trust_scores[user_id] = {belief: 0.0 for belief in TrustBeliefs}
        
        old_score = self.trust_scores[user_id][trust_belief]
        new_score = self.get_new_score_logarithmic(old_score, value, weight)
        self.trust_scores[user_id][trust_belief] = new_score
        
        self.log_trust_change(user_id, trust_belief, old_score, new_score, value, weight, message)
        
        self.save_trust_file() 
        print(f"DEBUG: Updated {trust_belief.name} for user {user_id}: {new_score}")
    
    def get_room(self, room_id):
        self.perceived_state.setdefault("rooms", {})
        self.perceived_state["rooms"].setdefault(room_id, {})
        return self.perceived_state["rooms"][room_id]
    
    def human_search_room(self, room_id):
        """
        Marks a room as searched by a human.
        """
        room = self.get_room(room_id)
        room["searched"] = 1
        
    def robot_search_room(self, room_id):
        """
        Marks a room as searched by a robot.
        """
        room = self.get_room(room_id)
        room["searched"] = 2
        
    def was_searched(self, room_id):
        """
        Returns the searched status of the room (0 if not set).
        """
        return self.perceived_state.get("rooms", {}).get(room_id, {}).get("searched", 0)
    
    def add_victim(self, room_id, victim, found=1):
        """
        Adds a victim to the room.
        """
        room = self.get_room(room_id)
        room.setdefault("victims", [])
        room["victims"].append({
            "victim": victim,
            "rescued": False,
            "found": found
        })
        
    def victims(self, room_id, rescued=None, found=None):
        """
        Returns a list of victims in the room that meet the specified criteria.
        """
        room = self.perceived_state.get("rooms", {}).get(room_id, {})
        victims_list = room.get("victims", [])
        if rescued is not None:
            victims_list = [v for v in victims_list if v["rescued"] == rescued]
        if found is not None:
            victims_list = [v for v in victims_list if v["found"] == found]
        return victims_list
        
    def update_victim(self, room_id, victim, rescued):
        """
        Updates the status of a victim in the room.
        """
        room = self.perceived_state.get("rooms", {}).get(room_id, {})
        for v in room.get("victims", []):
            if v["victim"] == victim:
                v["rescued"] = rescued
                break

    def plot_trust_evolution(self, user_id):
        """
        Reads the evolution log for a given user and plots the evolution
        of the six trust values over time. Horizontally is time, and each of the six
        lines represents a trust belief.
        """
        if not self.evolution_file.exists():
            print("No evolution log exists.")
            return

        evolution_data = {belief: [] for belief in TrustBeliefs}
        all_timestamps = []

        with self.evolution_file.open('r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == user_id:
                    try:
                        belief = TrustBeliefs[row['trust_belief']]
                    except KeyError:
                        continue
                    ts = datetime.fromisoformat(row['timestamp'])
                    new_score = float(row['new_score'])
                    evolution_data[belief].append((ts, new_score))
                    all_timestamps.append(ts)
        
        if not all_timestamps:
            print(f"No trust evolution data available for user: {user_id}")
            return  # Exit safely

        global_t0 = min(all_timestamps)  # Now safe to call

        
        def format_time(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"
        
        import matplotlib.ticker as ticker
        
        plt.figure(figsize=(10, 6))
        
        for belief, values in evolution_data.items():
            if values:
                values.sort(key=lambda x: x[0])
                times, scores = zip(*values)
                # Elapsed time (in seconds) relative to global_t0.
                elapsed = [(t - global_t0).total_seconds() for t in times]
                plt.plot(elapsed, scores, marker='o', label=belief.name)
        
        plt.xlabel("Time since First Change")
        plt.ylabel("Trust Score")
        plt.title(f"Trust Evolution for User {user_id}")
        plt.legend()
        plt.grid(True)
        
        ax = plt.gca()
        formatter = ticker.FuncFormatter(lambda x, pos: format_time(x))
        ax.xaxis.set_major_formatter(formatter)
    
        plt.savefig(self.evolution_folder / f"trust_evolution_{user_id}_{self.game_timestamp}.png")