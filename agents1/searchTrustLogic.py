import numpy as np
import random

def add_room_based_on_trust(agent, competence, room_name):
    """
    Decides whether to add a room to the agent's searched list based on human trust.

    :param agent: The instance of the BaselineAgent (or OfficialAgent)
    :param competence: The competence of the human in searching the room, finding victims or collecting victims.
    :param room_name: The name of the room being evaluated
    """
    # Scale competence to probability: (-1 to 1) -> (0 to 1)
    prob = (competence + 1) * 0.5  # Convert to probability scale (0% to 100%)
    
    # Random decision: trust probability vs. random roll
    rand = random.random()  # Generate a value between 0 and 1
    if rand <= prob:
        agent._searched_rooms.append(room_name)
        print(f"[SearchTrust] TRUST: Adding {room_name} (Competence: {competence}, Probability: {prob:.2f}, Roll: {rand:.2f})")
    else:
        print(f"[SearchTrust] NO TRUST: Ignoring {room_name} (Competence: {competence}, Probability: {prob:.2f}, Roll: {rand:.2f})")


def calculate_confidence(number_of_actions, constant):
        """
        Calculate confidence as a ratio of actions performed to a given constant.
        Ensures the value remains between 0 and 1.
        """
        return min(1.0, max(0.0, number_of_actions / constant))
    
def calculate_increment_with_confidence(number_of_actions, increment_value, confidence_constant=50):
    """
    Adjust the increment based on confidence.
    Formula: (1 - confidence) * increment_value
    
    The logic behind this: Looking through the POV of the current Willingness and Competence values,
    - Low confidence => You have low confidence in these values at the moment, so you will allow for large magnitude updates (the returned increment)
    - High confidence => You have high confidence in these values at the moment, so you won't allow for large magnitude updates (the returned increment)
    """
    confidence = calculate_confidence(number_of_actions, confidence_constant)
    return (1 - confidence) * increment_value


def update_search_willingness(agent, use_confidence=False):
    """
    Update the search willingness after the agent sends a room to the human.
    """
    base_increment = compute_search_willingness_update(len(agent._searched_rooms_claimed_by_human), len(agent._searched_rooms_by_agent))
    increment = calculate_increment_with_confidence(agent._number_of_actions_search, base_increment) if use_confidence else base_increment
    agent._trustBeliefs[agent._human_name]['search']['willingness'] = agent._search_willingness_start_value + increment
    agent._trustBeliefs[agent._human_name]['search']['willingness'] = np.clip(agent._trustBeliefs[agent._human_name]['search']['willingness'], -1, 1)
    print(f"[SearchTrust] Search willingness updated to {agent._trustBeliefs[agent._human_name]['search']['willingness']:.2f}")
    
    
def compute_search_willingness_update(X, Z):
    """
    X = num_searched_rooms_claimed_by_human
    Z = num_searched_rooms_by_agent
    Compute the willingness update based on the number of areas the human claimed to have searched and the number of areas the agent actually searched.
    """
    if Z == 0:
        return 0
    percentage = X / Z
    return (percentage - 0.7) * X / 2
    
    
def penalize_search_willingness_for_sending_rooms_already_searched(agent, area, use_confidence=False):
    """
    Penalize the agent's willingness to search if it sends rooms that the human has already
    claimed to have searched.
    """
    increment = calculate_increment_with_confidence(agent._number_of_actions_search, -0.1) if use_confidence else -0.1
    agent._trustBelief(agent._team_members, agent._trustBeliefs, agent._folder, 'search', 'willingness', increment)
    print(f"[SearchTrust] Penalizing search willingness for sending rooms already searched ({area}): {increment:.2f}")
    
    
def penalize_search_competence_for_claimed_searched_room_with_obstacle(agent, obstacle_type, use_confidence=False):
    """
    Penalize the agent's search competence if it finds an obstacle in a room that was claimed searched.
    """
    increment = calculate_increment_with_confidence(agent._number_of_actions_search, -0.2) if use_confidence else -0.2
    agent._trustBelief(agent._team_members, agent._trustBeliefs, agent._folder, 'search', 'competence', increment)
    agent._not_penalizable.append(agent._door['room_name']) # this area should not be penalized again in this search round
    print(f"[SearchTrust] Penalizing search competence for finding a {obstacle_type} in a claimed searched room {agent._door['room_name']}: {increment:.2f}")


def penalize_search_competence_for_claimed_searched_room_with_victim(agent, victim, use_confidence=False):
    """
    Penalize the agent's search competence if it finds a victim in a room that was claimed searched.
    """
    increment = calculate_increment_with_confidence(agent._number_of_actions_search, -0.2) if use_confidence else -0.2
    agent._trustBelief(agent._team_members, agent._trustBeliefs, agent._folder, 'search', 'competence', increment)
    agent._not_penalizable.append(agent._door['room_name']) # this area should not be penalized again in this search round
    print(f"[SearchTrust] Penalizing search competence for finding {victim} in a previously claimed searched room {agent._door['room_name']}: {increment:.2f}")


def reward_search_competence_for_claimed_searched_room(agent, area, use_confidence=False):
    """
    Reward the agent's search competence if it finds no obstacles or victims in a room that was claimed searched.
    """
    increment = calculate_increment_with_confidence(agent._number_of_actions_search, 0.1) if use_confidence else 0.1
    agent._trustBelief(agent._team_members, agent._trustBeliefs, agent._folder, 'search', 'competence', increment)
    print(f"[SearchTrust] Rewarding search competence for claiming a searched room ({area}): {increment:.2f}")
