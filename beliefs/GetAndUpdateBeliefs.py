import csv

def get_csv(filename):
    # results = []
    
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            key = row['name']
            value1 = float(row['competence'])
            value2 = float(row['willingness'])
            
            return (key, value1, value2)
    
    # return results

def update_csv(filename, key, value1, value2):
    with open(filename, mode='w', newline='') as file:
        fieldnames = ['name', 'competence', 'willingness']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)