import os
import glob
import csv
from datetime import datetime

def get_latest_experiment(log_dir='logs'):
    exp_dirs = glob.glob(os.path.join(log_dir, 'exp_*'))
    if not exp_dirs:
        return None
    
    # Sort by modification time and get the latest
    latest_exp = max(exp_dirs, key=os.path.getmtime)
    return latest_exp

def process_log_data(exp_dir):
    """Process log data from a specific experiment directory"""
    if not os.path.exists(exp_dir):
        print(f"Experiment directory not found: {exp_dir}")
        return None
    
    print(f"Processing experiment directory: {exp_dir}")
    
    # exp_type = os.path.basename(exp_dir).split('_')[1]  # normal or strong
    
    # Find the world_1 directory and its action log file
    world1_dir = os.path.join(exp_dir, 'world_1')
    if not os.path.exists(world1_dir):
        print(f"world_1 directory not found in {exp_dir}")
        return None
        
    action_files = glob.glob(os.path.join(world1_dir, '*.csv'))
    if not action_files:
        print(f"No action log files found in {world1_dir}")
        return None
    
    action_file = action_files[0]
    data = {
        'scores': [],
        'completeness': [],
        'rescuebot_actions': [],
        'human_actions': [],
        'ticks': []
    }
    
    with open(action_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # remove header
        
        for row in reader:
            try:
                data['scores'].append(float(row[0]))
                data['completeness'].append(float(row[1]))
                data['rescuebot_actions'].append(row[2] if row[2] else None)
                data['human_actions'].append(row[4] if row[4] else None)
                data['ticks'].append(int(row[7]))
            except (IndexError, ValueError) as e:
                print(f"Error processing row: {e}")
                continue
    
    return data
def analyze_movement_patterns(data):
    """Analyze movement patterns of both agents"""
    movement_patterns = {
        'rescuebot': {'idle': 0, 'north': 0, 'south': 0, 'east': 0, 'west': 0, 'diagonal': 0},
        'human': {'idle': 0, 'north': 0, 'south': 0, 'east': 0, 'west': 0, 'diagonal': 0}
    }
    
    for action in data['rescuebot_actions']:
        if not action:
            movement_patterns['rescuebot']['idle'] += 1
        elif 'North' in action and ('East' in action or 'West' in action):
            movement_patterns['rescuebot']['diagonal'] += 1
        elif 'South' in action and ('East' in action or 'West' in action):
            movement_patterns['rescuebot']['diagonal'] += 1
        elif 'North' in action:
            movement_patterns['rescuebot']['north'] += 1
        elif 'South' in action:
            movement_patterns['rescuebot']['south'] += 1
        elif 'East' in action:
            movement_patterns['rescuebot']['east'] += 1
        elif 'West' in action:
            movement_patterns['rescuebot']['west'] += 1
            
    for action in data['human_actions']:
        if not action:
            movement_patterns['human']['idle'] += 1
        elif 'North' in action and ('East' in action or 'West' in action):
            movement_patterns['human']['diagonal'] += 1
        elif 'South' in action and ('East' in action or 'West' in action):
            movement_patterns['human']['diagonal'] += 1
        elif 'North' in action:
            movement_patterns['human']['north'] += 1
        elif 'South' in action:
            movement_patterns['human']['south'] += 1
        elif 'East' in action:
            movement_patterns['human']['east'] += 1
        elif 'West' in action:
            movement_patterns['human']['west'] += 1
            
    return movement_patterns

def analyze_interaction_phases(data):
    """Analyze different phases of interaction between agents"""
    phases = []
    current_phase = {'start': 0, 'type': 'unknown', 'duration': 0}
    
    for i in range(len(data['ticks'])):
        rescuebot_action = data['rescuebot_actions'][i]
        human_action = data['human_actions'][i]
        
        # phase types
        if rescuebot_action and human_action:
            phase_type = 'collaborative'
        elif rescuebot_action and not human_action:
            phase_type = 'rescuebot_solo'
        elif not rescuebot_action and human_action:
            phase_type = 'human_solo'
        else:
            phase_type = 'idle'
            
        # new phase check
        if i == 0 or phase_type != current_phase['type']:
            if i > 0:
                phases.append(current_phase)
            current_phase = {'start': data['ticks'][i], 'type': phase_type, 'duration': 1}
        else:
            current_phase['duration'] += 1
            
    phases.append(current_phase)
    return phases

def analyze_object_interaction(data):
    """Analyze object interactions and removal patterns"""
    object_interactions = {
        'rescuebot': {'remove_count': 0, 'remove_sequences': []},
        'human': {'remove_count': 0, 'remove_sequences': []}
    }
    
    current_sequence = {'agent': None, 'start': 0, 'duration': 0}
    
    for i in range(len(data['ticks'])):
        rescuebot_action = data['rescuebot_actions'][i]
        human_action = data['human_actions'][i]
        
        if rescuebot_action == 'RemoveObject':
            object_interactions['rescuebot']['remove_count'] += 1
            if current_sequence['agent'] != 'rescuebot':
                if current_sequence['agent']:
                    object_interactions[current_sequence['agent']]['remove_sequences'].append(current_sequence)
                current_sequence = {'agent': 'rescuebot', 'start': data['ticks'][i], 'duration': 1}
            else:
                current_sequence['duration'] += 1
                
        elif human_action == 'RemoveObject':
            object_interactions['human']['remove_count'] += 1
            if current_sequence['agent'] != 'human':
                if current_sequence['agent']:
                    object_interactions[current_sequence['agent']]['remove_sequences'].append(current_sequence)
                current_sequence = {'agent': 'human', 'start': data['ticks'][i], 'duration': 1}
            else:
                current_sequence['duration'] += 1
                
    if current_sequence['agent']:
        object_interactions[current_sequence['agent']]['remove_sequences'].append(current_sequence)
        
    return object_interactions

def analyze_data(data):
    if not data:
        return
    
    # metrics
    total_ticks = max(data['ticks'])
    final_score = data['scores'][-1]
    final_completeness = data['completeness'][-1]
    rescuebot_action_count = sum(1 for action in data['rescuebot_actions'] if action)
    human_action_count = sum(1 for action in data['human_actions'] if action)
    
    # details
    movement_patterns = analyze_movement_patterns(data)
    interaction_phases = analyze_interaction_phases(data)
    object_interactions = analyze_object_interaction(data)
    

    print("\n=== Mission Overview ===")
    print(f"Total mission time (ticks): {total_ticks}")
    print(f"Final score: {final_score}")
    print(f"Final completeness: {final_completeness:.2f}%")
    
    print("\n=== Agent Activity ===")
    print(f"Rescuebot actions: {rescuebot_action_count} ({rescuebot_action_count/total_ticks:.3f} per tick)")
    print(f"Human actions: {human_action_count} ({human_action_count/total_ticks:.3f} per tick)")
    
    print("\n=== Movement Analysis ===")
    for agent in ['rescuebot', 'human']:
        print(f"\n{agent.capitalize()} movement breakdown:")
        total_moves = sum(movement_patterns[agent].values())
        for move_type, count in movement_patterns[agent].items():
            percentage = (count/total_moves * 100) if total_moves > 0 else 0
            print(f"  {move_type.capitalize()}: {count} ({percentage:.1f}%)")
    
    print("\n=== Interaction Phases ===")
    phase_counts = {'collaborative': 0, 'rescuebot_solo': 0, 'human_solo': 0, 'idle': 0}
    for phase in interaction_phases:
        phase_counts[phase['type']] += phase['duration']
    
    for phase_type, duration in phase_counts.items():
        percentage = (duration/total_ticks * 100)
        print(f"{phase_type.capitalize()}: {duration} ticks ({percentage:.1f}%)")
    
    print("\n=== Object Interactions ===")
    for agent in ['rescuebot', 'human']:
        print(f"\n{agent.capitalize()}:")
        print(f"  Total object removals: {object_interactions[agent]['remove_count']}")
        if object_interactions[agent]['remove_sequences']:
            avg_sequence = sum(seq['duration'] for seq in object_interactions[agent]['remove_sequences']) / len(object_interactions[agent]['remove_sequences'])
            print(f"  Average sequence duration: {avg_sequence:.1f} ticks")
            print(f"  Number of removal sequences: {len(object_interactions[agent]['remove_sequences'])}")

def main():
    # Process log data from the latest experiment
    data = process_log_data('baselines/custom/')
    
    if data:
        analyze_data(data)
    else:
        print("Failed to process log data!")

if __name__ == "__main__":
    main()
