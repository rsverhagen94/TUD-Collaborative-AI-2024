import os, requests
import sys
import csv
import glob
import pathlib

def output_logger(fld):
    recent_dir = max(glob.glob(os.path.join(fld, '*/')), key=os.path.getmtime)
    recent_dir = max(glob.glob(os.path.join(recent_dir, '*/')), key=os.path.getmtime)
    action_files = glob.glob(os.path.join(recent_dir, 'world_1/action*'))
    if action_files:
        action_file = action_files[0]
    else:
        print(f"No action files found in {os.path.join(recent_dir, 'world_1')}")
        return
    action_header = []
    action_contents=[]
    trustfile_header = []
    trustfile_contents = []
    # Calculate the unique human and agent actions
    unique_agent_actions = []
    unique_human_actions = []
    objects_removed_together = 0
    objects_removed_alone = 0
    victims_rescued_together = 0
    victims_rescued_alone = 0

    with open(action_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        prev_row = [None,None,None,None,None,None]
        for row in reader:
            if action_header==[]:
                action_header=row
                continue
            if row[2:4] not in unique_agent_actions and row[2]!="":
                unique_agent_actions.append(row[2:4])
            if row[4:6] not in unique_human_actions and row[4]!="":
                unique_human_actions.append(row[4:6])
            if row[4] == 'RemoveObjectTogether' or row[4] == 'CarryObjectTogether' or row[4] == 'DropObjectTogether':
                if row[4:6] not in unique_agent_actions:
                    unique_agent_actions.append(row[4:6])

            if row[2] == 'RemoveObjectTogether' and prev_row[2] != 'RemoveObjectTogether':
                objects_removed_together += 1
            if row[4] == 'RemoveObjectTogether' and prev_row[4] != 'RemoveObjectTogether':
                objects_removed_together += 1

            if row[2] == 'RemoveObject' and prev_row[2] != 'RemoveObject':
                objects_removed_alone += 1
            if row[4] == 'RemoveObject' and prev_row[4] != 'RemoveObject':
                objects_removed_alone += 1

            # If the score increased, we must've rescued a victim
            if row[2] == 'DropObjectTogether' and prev_row[0] < row[0]:
                victims_rescued_together += 1
            if row[4] == 'DropObjectTogether' and prev_row[0] < row[0]:
                victims_rescued_together += 1

            if row[2] == 'Drop' and prev_row[0] < row[0]:
                victims_rescued_alone += 1
            if row[4] == 'Drop' and prev_row[0] < row[0]:
                victims_rescued_alone += 1

            prev_row = row

            res = {action_header[i]: row[i] for i in range(len(action_header))}
            action_contents.append(res)

    with open(fld+'/beliefs/currentTrustBelief.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in reader:
            if trustfile_header==[]:
                trustfile_header=row
                continue
            if row:
                res = {trustfile_header[i] : row[i] for i in range(len(trustfile_header))}
                trustfile_contents.append(res)
    
    # Retrieve the number of ticks to finish the task, score, and completeness
    no_ticks = action_contents[-1]['tick_nr']
    score = action_contents[-1]['score']
    completeness = action_contents[-1]['completeness']
    # Save the output as a csv file
    print("Saving output...")
    with open(os.path.join(recent_dir,'world_1/output.csv'),mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['completeness','score','no_ticks','agent_actions','human_actions','objects_removed_alone',
                             'objects_removed_together','victims_rescued_alone','victims_rescued_together'])
        csv_writer.writerow([completeness,score,no_ticks,len(unique_agent_actions),len(unique_human_actions),
                             objects_removed_alone,objects_removed_together,victims_rescued_alone,
                             victims_rescued_together
                             ])
        
    # Update the trust belief values
    trust_file_path = fld + '/beliefs/allTrustBeliefs.csv'
    
    # Open trust file and remove the old human rows
    with open(trust_file_path, mode='r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        trustfile_header = next(reader)  # Read header
        updated_trust = [row for row in reader if row[0] != trustfile_contents[0]['name']]  # Remove old human rows
    
    # Write back the updated data with new trust values
    with open(trust_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(trustfile_header)  # Write header
        csv_writer.writerows(updated_trust + [[t['name'], t['task'], t['competence'], t['willingness']] for t in trustfile_contents])  # Append new data