import matplotlib.pyplot as plt
import numpy as np
from analysis import process_log_data, get_latest_experiment
import os

def plot_score_comparison(data1, data2, label1="Run 1", label2="Run 2"):
    plt.figure(figsize=(10, 6))
    plt.plot(data1['ticks'], data1['scores'], label=label1)
    plt.plot(data2['ticks'], data2['scores'], label=label2)
    plt.xlabel('Time (ticks)')
    plt.ylabel('Score')
    plt.title('Score Progression Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('score_comparison.png')
    plt.close()

def plot_completeness_comparison(data1, data2, label1="Run 1", label2="Run 2"):
    plt.figure(figsize=(10, 6))
    plt.plot(data1['ticks'], data1['completeness'], label=label1)
    plt.plot(data2['ticks'], data2['completeness'], label=label2)
    plt.xlabel('Time (ticks)')
    plt.ylabel('Completeness (%)')
    plt.title('Mission Completeness Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('completeness_comparison.png')
    plt.close()

def plot_movement_patterns(data1, data2, label1="Run 1", label2="Run 2"):
    def get_movement_counts(data):
        movements = {'idle': 0, 'north': 0, 'south': 0, 'east': 0, 'west': 0, 'diagonal': 0}
        for action in data['rescuebot_actions']:
            if not action:
                movements['idle'] += 1
            elif 'North' in str(action) and ('East' in str(action) or 'West' in str(action)):
                movements['diagonal'] += 1
            elif 'South' in str(action) and ('East' in str(action) or 'West' in str(action)):
                movements['diagonal'] += 1
            elif 'North' in str(action):
                movements['north'] += 1
            elif 'South' in str(action):
                movements['south'] += 1
            elif 'East' in str(action):
                movements['east'] += 1
            elif 'West' in str(action):
                movements['west'] += 1
        return movements

    movements1 = get_movement_counts(data1)
    movements2 = get_movement_counts(data2)

    categories = list(movements1.keys())
    values1 = [movements1[cat] for cat in categories]
    values2 = [movements2[cat] for cat in categories]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, values1, width, label=label1)
    ax.bar(x + width/2, values2, width, label=label2)

    ax.set_ylabel('Count')
    ax.set_title('Movement Pattern Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('movement_patterns_comparison.png')
    plt.close()

def plot_interaction_phases(data1, data2, label1="Run 1", label2="Run 2"):
    def count_interaction_types(data):
        collaborative = 0
        solo_rescuebot = 0
        solo_human = 0
        idle = 0
        
        for i in range(len(data['ticks'])):
            rescuebot_action = data['rescuebot_actions'][i]
            human_action = data['human_actions'][i]
            
            if rescuebot_action and human_action:
                collaborative += 1
            elif rescuebot_action and not human_action:
                solo_rescuebot += 1
            elif not rescuebot_action and human_action:
                solo_human += 1
            else:
                idle += 1
                
        return {
            'Collaborative': collaborative,
            'Rescuebot Solo': solo_rescuebot,
            'Human Solo': solo_human,
            'Idle': idle
        }

    phases1 = count_interaction_types(data1)
    phases2 = count_interaction_types(data2)

    categories = list(phases1.keys())
    values1 = [phases1[cat] for cat in categories]
    values2 = [phases2[cat] for cat in categories]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, values1, width, label=label1)
    ax.bar(x + width/2, values2, width, label=label2)

    ax.set_ylabel('Number of Ticks')
    ax.set_title('Interaction Phases Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('interaction_phases_comparison.png')
    plt.close()

def visualize_comparison(log_dir1, log_dir2, label1="Default Trust", label2="Custom Trust"):
    """
    Create comparative visualizations between two experiment runs
    """
    data1 = process_log_data(log_dir1)
    data2 = process_log_data(log_dir2)
    
    if not data1 or not data2:
        print("Error: Could not process log data from one or both directories")
        return
    
    # Create visualizations
    plot_score_comparison(data1, data2, label1, label2)
    plot_completeness_comparison(data1, data2, label1, label2)
    plot_movement_patterns(data1, data2, label1, label2)
    plot_interaction_phases(data1, data2, label1, label2)
    
    print("Visualizations have been created and saved as PNG files in the current directory.")

if __name__ == "__main__":
    # For now, let's just visualize the latest experiment data
    latest_exp = get_latest_experiment()
    if latest_exp:
        print(f"Using latest experiment: {latest_exp}")
        data = process_log_data(latest_exp)
        if data:
            # Create single experiment visualizations
            plt.figure(figsize=(10, 6))
            plt.plot(data['ticks'], data['scores'], label='Score')
            plt.xlabel('Time (ticks)')
            plt.ylabel('Score')
            plt.title('Score Progression')
            plt.legend()
            plt.grid(True)
            plt.savefig('score_progression.png')
            plt.close()
            
            plt.figure(figsize=(10, 6))
            plt.plot(data['ticks'], data['completeness'], label='Completeness')
            plt.xlabel('Time (ticks)')
            plt.ylabel('Completeness (%)')
            plt.title('Mission Completeness')
            plt.legend()
            plt.grid(True)
            plt.savefig('mission_completeness.png')
            plt.close()
            
            print("Created visualizations for the latest experiment.")
            print("Once you have data from multiple runs, you can use visualize_comparison() to compare them.")
        else:
            print("Could not process experiment data")
    else:
        print("No experiment directories found!")
