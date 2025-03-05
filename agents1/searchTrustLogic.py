import numpy as np

def compute_search_willingness_update(X, Z, confidence_level):
    """
    X = num_searched_rooms_claimed_by_human
    Z = num_searched_rooms_by_agent
    Compute the willingness update based on the number of areas the human claimed to have searched and the number of areas the agent actually searched.
    """
    # Compute the difference between the number of areas the human claimed to have searched and the number of areas the agent actually searched
    Y = max(1, Z // 2)
    # Adjust willingness proportionally
    diff = X - Y
    return confidence_level * 0.2 * np.tanh(0.2 * diff)
    
def compute_search_competence_penalty_for_obstacle(obstacle_type, confidence_level):
    """
    obstacle_type = 'rock', 'tree', or 'stone'.
    Return how much to penalize the human's search competence
    if the agent finds an obstacle in a room that was claimed searched.
    """
    return -0.1 * confidence_level

def compute_search_competence_penalty_for_victim(victim_type, confidence_level):
    """
    victim_type = 'mild' / 'critical'
    Return a negative increment for discovering that
    a supposedly searched room still had a victim.
    """
    return -0.1 * confidence_level

def compute_search_competence_reward_no_victims_or_obstacles(confidence_level):
    """
    Return a reward for when the agent re-searches a room claimed by the human
    and finds no obstacles/victims (i.e., the human was correct).
    """
    return 0.1 * confidence_level

def compute_search_competence_bonus_collect_all_victims(num_searched_rooms_claimed_by_human, confidence_level):
    """
    When all 8 victims are rescued, return a bonus
    to competence.
    """
    # Since the rest of the rooms are assumed to be searched, we can use log to prevent overly large updates
    return confidence_level * 0.1 * np.log(num_searched_rooms_claimed_by_human + 1)