from enum import Enum
import os

class TrustBeliefs(Enum):
    SEARCH_WILLINGNESS = 1
    SEARCH_COMPETENCE = 2
    RESCUE_WILLINGNESS = 3
    RESCUE_COMPETENCE = 4

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
            #         TrustBeliefs.RESCUE_COMPETENCE: 0.55
            #     },
            #     ...
            # }
        """
        
        self.csv_file = 'trust/trust_scores.csv'
        self.trust_scores = {}
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)

    def create_trust_file(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'user_id',
                    'search_willingness',
                    'search_competence',
                    'rescue_willingness',
                    'rescue_competence'
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
                    TrustBeliefs.RESCUE_COMPETENCE: float(row['rescue_competence'])
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
                'rescue_competence'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user_id, score in existing_scores.items():
                writer.writerow({
                    'user_id': user_id,
                    'search_willingness': score[TrustBeliefs.SEARCH_WILLINGNESS],
                    'search_competence': score[TrustBeliefs.SEARCH_COMPETENCE],
                    'rescue_willingness': score[TrustBeliefs.RESCUE_WILLINGNESS],
                    'rescue_competence': score[TrustBeliefs.RESCUE_COMPETENCE]
                })
        
    def trigger_trust_change(self, trust_belief, user_id, value):
        # Update trust score based on stuff
        pass