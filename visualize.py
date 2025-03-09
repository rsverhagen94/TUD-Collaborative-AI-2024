import matplotlib.pyplot as plt
import numpy as np
from analysis import process_log_data, get_latest_experiment
import os
from typing import List, Dict

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
    plt.close('all')

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
    plt.close('all')

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
    plt.close('all')

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
    plt.close('all')

def visualize_comparison(log_dir1, log_dir2, label1="Default Trust", label2="Custom Trust"):
    """
    Create comparative visualizations between two experiment runs
    """
    data1 = process_log_data(log_dir1)
    data2 = process_log_data(log_dir2)
    
    if not data1 or not data2:
        print("Error: Could not process log data from one or both directories")
        return
    
    plot_score_comparison(data1, data2, label1, label2)
    plot_completeness_comparison(data1, data2, label1, label2)
    plot_movement_patterns(data1, data2, label1, label2)
    plot_interaction_phases(data1, data2, label1, label2)
    
    print("Visualizations have been created and saved as PNG files in the current directory.")

def plot_idle_actions_and_events(custom_log_dir: str, baseline_logs: Dict[str, str]):
    """Create a plot showing percentage of idle actions over time with event markers
    for victim rescues, comparing custom trust mechanism against baselines.
    
    Args:
        custom_log_dir: Directory containing logs for custom trust mechanism
        baseline_logs: Dictionary mapping baseline names to their log directories
    """
    plt.figure(figsize=(12, 6))
    
    # Process custom trust data first
    data_dict = {
        'Custom Trust': process_log_data(custom_log_dir)
    }
    # Add baseline data
    for name, log_dir in baseline_logs.items():
        data_dict[name] = process_log_data(log_dir)
    
    # Define colors for each run
    colors = {
        'Custom Trust': 'blue',
        'Never Trust': 'red',
        'Always Trust': 'green',
        'Dynamic Trust': 'purple'
    }
    
    # Process all datasets
    for label, data in data_dict.items():
        if not data:
            print(f"Warning: Could not process data for {label}")
            continue
            
        # Calculate idle percentage in windows
        window_size = 20  # over 20 tick windows
        idle_percentages = []
        tick_windows = []
        
        for i in range(0, len(data['ticks']), window_size):
            window_end = min(i + window_size, len(data['ticks']))
            window_actions = data['rescuebot_actions'][i:window_end] + data['human_actions'][i:window_end]
            idle_count = sum(1 for action in window_actions if not action)
            idle_percentage = (idle_count / (2 * (window_end - i))) * 100  # Times 2 because we count both agents
            idle_percentages.append(idle_percentage)
            tick_windows.append(data['ticks'][i])
        
        color = colors.get(label, 'gray')  # Use gray as fallback color
        
        # Plot idle time
        plt.plot(tick_windows, idle_percentages, label=f'{label} Idle %', color=color)
        
        # Plot rescue events
        for i in range(1, len(data['ticks'])):
            tick = data['ticks'][i]
            if i > 0 and (data['scores'][i] - data['scores'][i-1]) > 0:
                plt.axvline(x=tick, color=color, alpha=0.3, linestyle='--')
                plt.scatter(tick, 0, color=color, marker='*', s=100, 
                          label=f'{label} Rescue' if i == 1 else '')
    
    plt.xlabel('Time (ticks)')
    plt.ylabel('Idle Actions (%)')
    plt.title('Idle Actions Percentage Over Time with Rescue Events')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('idle_actions_comparison.png', bbox_inches='tight')
    plt.close('all')

def plot_trust_comparison(custom_log_dir: str, baseline_logs: Dict[str, str], metrics: List[str] = None):
    """Plot comparison between custom trust mechanism and baselines.
    
    Args:
        custom_log_dir: Directory containing logs for custom trust mechanism
        baseline_logs: Dictionary mapping baseline names to their log directories
        metrics: List of metrics to plot. If None, defaults to ['completeness', 'human_actions', 'agent_actions']
    """
    if metrics is None:
        metrics = ['completeness', 'human_actions', 'agent_actions']
    
    # Process all data
    data_dict = {
        'Custom Trust': process_log_data(custom_log_dir)
    }
    for name, log_dir in baseline_logs.items():
        data_dict[name] = process_log_data(log_dir)
    
    colors = {
        'Custom Trust': 'blue',
        'Never Trust': 'red',
        'Always Trust': 'green',
        'Random Trust': 'purple'
    }
    
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        
        for name, data in data_dict.items():
            if data is None:
                print(f"Warning: Could not process data for {name}")
                continue
                
            if metric == 'completeness':
                y_values = data['completeness']
                ylabel = 'Mission Completeness (%)'
            elif metric == 'human_actions':
                y_values = [sum(1 for action in data['human_actions'][:i+1] if action) 
                           for i in range(len(data['human_actions']))]
                ylabel = 'Cumulative Human Actions'
            elif metric == 'agent_actions':
                y_values = [sum(1 for action in data['rescuebot_actions'][:i+1] if action) 
                           for i in range(len(data['rescuebot_actions']))]
                ylabel = 'Cumulative Agent Actions'
            
            plt.plot(data['ticks'], y_values, 
                     label=name, color=colors.get(name, 'gray'),
                     alpha=0.8)
        
        plt.xlabel('Time (ticks)')
        plt.ylabel(ylabel)
        plt.title(f'{metric.replace("_", " ").title()} Over Time')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'trust_comparison_{metric}.png')
        plt.close('all')

if __name__ == "__main__":
    baseline_logs = {
        'Never Trust': 'baselines/never/',
        'Always Trust': 'baselines/always/',
        'Random Trust': 'baselines/random/'
    }
    
    #not using latest now
    latest_exp = get_latest_experiment()
    if latest_exp:
        print(f"Using latest experiment: {latest_exp}")
        plot_trust_comparison('baselines/custom/', baseline_logs)
        plt.close('all')
        
        data = process_log_data( 'baselines/custom/')
        
        if data is not None:
            plt.figure(figsize=(10, 6))
            plt.plot(data['ticks'], data['completeness'], label='Completeness')
            plt.xlabel('Time (ticks)')
            plt.ylabel('Completeness (%)')
            plt.title('Mission Completeness')
            plt.legend()
            plt.grid(True)
            plt.savefig('mission_completeness.png')
            plt.close('all')
            
            plot_idle_actions_and_events('baselines/custom/', baseline_logs)
            
            print("Created visualizations for the latest experiment:")
            print("1. score_progression.png - Shows how the score changes over time")
            print("2. mission_completeness.png - Shows mission completion progress")
            print("3. idle_actions_comparison.png - Shows idle actions % with event markers")
            print("\nOnce you have data from multiple runs, you can use visualize_comparison() to compare them.")
        else:
            print("Could not process data from the latest experiment.")
    else:
        print("No experiment directories found!")
