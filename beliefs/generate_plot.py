import csv
import matplotlib.pyplot as plt

timestamps = []
competency_rescue_severelyInjured = []
competency_rescue_mildlyInjured = []
competency_arrival = []
willingness_search = []
willingness_response = []
willingness_rescue = []
score = []
completeness = []

ticks = []

with open('actions.csv', 'r') as file:
    reader = csv.DictReader(file, delimiter=';')

    for row in reader:
        competency_rescue_severelyInjured.append(float(row['competency_rescue_severelyInjured']))
        competency_rescue_mildlyInjured.append(float(row['competency_rescue_mildlyInjured']))
        competency_arrival.append(float(row['competency_arrival']))
        willingness_search.append(float(row['willingness_search']))
        willingness_response.append(float(row['willingness_response']))
        willingness_rescue.append(float(row['willingness_rescue']))

        score.append(float(row['score']))
        completeness.append(float(row['completeness']))
        ticks.append(float(row['tick_nr']))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

fig.suptitle('Alice', fontsize=14)

ax1.plot(ticks, competency_rescue_severelyInjured, label='competency_rescue_severelyInjured')
ax1.plot(ticks, competency_rescue_mildlyInjured, label='competency_rescue_mildlyInjured')
ax1.plot(ticks, competency_arrival, label='competency_arrival')
ax1.plot(ticks, willingness_search, label='willingness_search')
ax1.plot(ticks, willingness_response, label='willingness_response')
ax1.plot(ticks, willingness_rescue, label='willingness_rescue')

ax1.set_title('Beliefs')
ax1.set_ylim(-1, 1)
ax1.legend()
ax1.grid(True)

ax2.plot(ticks, score, label='score')
ax2.plot(ticks, completeness, label='completeness')

ax2.set_title('Progress')
ax1.set_ylim(0, 1)
ax2.set_xlabel('Tick')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()
