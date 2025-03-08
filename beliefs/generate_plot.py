import csv
import matplotlib.pyplot as plt

timestamps = []
competency_rescue_severelyInjured = []
competency_rescue_mildlyInjured = []
competency_arrival = []
willingness_search = []
willingness_response = []
willingness_rescue = []

with open('allTrustBeliefs.csv', 'r') as file:
    reader = csv.DictReader(file, delimiter=';')

    for row in reader:
        competency_rescue_severelyInjured.append(float(row['competency_rescue_severelyInjured']))
        competency_rescue_mildlyInjured.append(float(row['competency_rescue_mildlyInjured']))
        competency_arrival.append(float(row['competency_arrival']))
        willingness_search.append(float(row['willingness_search']))
        willingness_response.append(float(row['willingness_response']))
        willingness_rescue.append(float(row['willingness_rescue']))

plt.figure(figsize=(10, 6))

timestamps = range(len(competency_rescue_severelyInjured))
plt.plot(timestamps, competency_rescue_severelyInjured, label='competency_rescue_severelyInjured')
plt.plot(timestamps, competency_rescue_mildlyInjured, label='competency_rescue_mildlyInjured')
plt.plot(timestamps, competency_arrival, label='competency_arrival')
plt.plot(timestamps, willingness_search, label='willingness_search')
plt.plot(timestamps, willingness_response, label='willingness_response')
plt.plot(timestamps, willingness_rescue, label='willingness_rescue')

plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Beliefs over time')
plt.legend()
plt.tight_layout()
plt.show()
