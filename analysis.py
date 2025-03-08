import os
import glob
import csv
from datetime import datetime

def get_latest_experiment(log_dir='logs'):
    # Get all experiment directories
    exp_dirs = glob.glob(os.path.join(log_dir, 'exp_*'))
    if not exp_dirs:
        return None
    
    # Sort by modification time and get the latest
    latest_exp = max(exp_dirs, key=os.path.getmtime)
    return latest_exp

def process_log_data(log_dir='logs'):
    latest_exp = get_latest_experiment(log_dir)
    if not latest_exp:
        print("No experiment directories found!")
        return None
    
    # Get the experiment type from directory name
    exp_type = os.path.basename(latest_exp).split('_')[1]  # normal or strong
    
    # Find the world_1 directory and its action log file
    world1_dir = os.path.join(latest_exp, 'world_1')
    if not os.path.exists(world1_dir):
        print(f"world_1 directory not found in {latest_exp}")
        return None
        
    action_files = glob.glob(os.path.join(world1_dir, 'action*.csv'))
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
    
    # Read and process the action log
    with open(action_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Skip header
        
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
def analyze_data(data):
    if not data:
        return
    
    # Calculate metrics
    total_ticks = max(data['ticks'])
    final_score = data['scores'][-1]
    final_completeness = data['completeness'][-1]
    
    # Count non-None actions
    rescuebot_action_count = sum(1 for action in data['rescuebot_actions'] if action)
    human_action_count = sum(1 for action in data['human_actions'] if action)
    
    # Print analysis
    print("\nAnalysis Results:")
    print(f"Total mission time (ticks): {total_ticks}")
    print(f"Final score: {final_score}")
    print(f"Final completeness: {final_completeness:.2f}%")
    print(f"Number of rescuebot actions: {rescuebot_action_count}")
    print(f"Number of human actions: {human_action_count}")
    
    # Calculate action rates
    print(f"\nAction rates:")
    print(f"Rescuebot actions per tick: {rescuebot_action_count/total_ticks:.3f}")
    print(f"Human actions per tick: {human_action_count/total_ticks:.3f}")
    
    # Print progression of completeness
    print("\nCompleteness progression:")
    for i in range(0, len(data['ticks']), max(1, len(data['ticks'])//10)):
        print(f"Tick {data['ticks'][i]}: {data['completeness'][i]:.2f}%")

def main():
    # Process log data from the latest experiment
    data = process_log_data()
    
    if data:
        analyze_data(data)
    else:
        print("Failed to process log data!")

if __name__ == "__main__":
    main()
